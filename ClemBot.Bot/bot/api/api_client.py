import asyncio
import json
import logging
import queue
import typing as t
from http import HTTPStatus
from urllib.parse import quote

import aiohttp

import bot.bot_secrets as bot_secrets
from bot.consts import Urls
from bot.errors import ApiClientRequestError, BotOnlyRequestError

log = logging.getLogger(__name__)

RECONNECT_TIMEOUT = 10

connect_lock = asyncio.Lock()


class Result:
    def __init__(self, status: int, value: t.Any):
        self.status = status
        self.value = value

    def __str__(self):
        return f'Result Status: {self.status}\nValue:\n{json.dumps(self.value, indent=2)}'


class HttpRequestType:
    get = 'GET'
    put = 'PUT'
    post = 'POST'
    delete = 'DELETE'
    patch = 'PATCH'


class ApiClient:

    def __init__(self, *,
                 connect_callback=None,
                 disconnect_callback=None,
                 bot_only: bool = False):

        self.auth_token: str
        self.session: t.Optional[aiohttp.ClientSession] = None
        self.connected: bool = False
        self.headers: t.Dict[str, str] = None

        self._is_reconnecting: bool = False

        self.request_queue: queue.Queue = None

        self.bot_only = bot_only

        # Create an empty async method so our callback doesnt throw when we await it
        async def async_stub():
            pass

        # Specify a callback to alert the creation context of connection events
        self.connect_callback = connect_callback or async_stub

        # Specify a callback to alert the creation context of disconnection events
        self.disconnect_callback = disconnect_callback or async_stub

    @staticmethod
    def _build_url(url: str):
        url = f'{bot_secrets.secrets.api_url}{Urls.base_api_url}{quote(url)}'
        log.info('Building URL: {url}', url=url)
        return url

    async def close(self) -> None:
        """Close the aiohttp session."""
        await self.session.close()

    async def connect(self):
        if self.bot_only:
            raise BotOnlyRequestError("Request Failed: Bot is in bot_only mode")

        await self._internal_connect()

    async def _reconnect(self):

        # Asynchronously lock here to make sure
        # that only one task is checking the connection status at a time
        # otherwise we will have multiple tasks attempting to connect
        async with connect_lock:
            if not self.connected:
                return

            self.connected = False

        # Invoke the disconnect callback here after we know that no other tasks are going
        # to reach this point
        await self.disconnect_callback()

        log.info('Beginning ClemBot.Api reconnect request')
        await self._internal_connect()

    async def _internal_connect(self):
        log.info('Connecting to ClemBot.Api at URL: {url}', url=bot_secrets.secrets.api_url)

        # Check if we have an active session, this means we are trying to reconnect
        # if we are, do nothing
        if not self.session:
            self.session = aiohttp.ClientSession(raise_for_status=False)

        # Loop infinitely checking the api every RECONNECT_TIMEOUT seconds
        # Once auth succeeds then we allow other requests
        while not self.connected:
            self.connected = await self._authorize()

            if self.connected:
                log.info('Connecting to ClemBot.Api succeeded')
                await self.connect_callback()
                break

            log.error('Connecting to ClemBot.Api failed, retrying in {reconnect_timeout} seconds',
                      reconnect_timeout=RECONNECT_TIMEOUT)
            await asyncio.sleep(RECONNECT_TIMEOUT)

    async def _disconnected(self):
        log.warning('ClemBot.Api disconnected')
        await self._reconnect()

    async def _get_auth_token(self) -> t.Optional[str]:

        auth_args = {
            'method': HttpRequestType.get,
            'ssl': False,
            'url': self._build_url('bot/authorize'),
            'headers': {'Accept': '*/*'},
            'params': {'key': bot_secrets.secrets.api_key}
        }

        try:
            async with self.session.request(**auth_args) as resp:

                if resp.status == HTTPStatus.OK:
                    log.info('JWT Bearer token received')
                    return (await resp.json())['token']

                if resp.status == HTTPStatus.FORBIDDEN:
                    log.error('JWT Auth denied, Invalid API key')

        except aiohttp.ClientConnectorError as e:
            log.exception('Error: ClemBot.Api not found')
            return

    async def _authorize(self) -> bool:
        log.info('Requesting ClemBot.Api Access token')

        self.auth_token = await self._get_auth_token()

        if not self.auth_token:
            return False

        self.headers = {
            'Authorization': f'BEARER {self.auth_token}',
            'Content-type': 'application/json',
            'Accept': 'application/json'
        }

        log.info('Initialized JWT BEARER token Auth Headers')
        return True

    async def _request(self, http_type: str, endpoint: str, raise_on_error, params=None, body=None):

        log.info('HTTP {http_type} Request initializing to route: {endpoint}', http_type=http_type, endpoint=endpoint)

        req_args = {
            'method': http_type,
            'ssl': False,
            'url': self._build_url(endpoint),
            'raise_for_status': raise_on_error,
            'headers': self.headers,
            'params': params
        }

        if body:
            req_args['json'] = body

        async with self.session.request(**req_args) as resp:
            if resp.status == HTTPStatus.OK:
                data = await resp.json()
                log.info('{type} Request at endpoint "{endpoint}" with request data:{body}  Succeeded with response data:{data}',
                         type=http_type,
                         endpoint=endpoint,
                         body=body,
                         data=data)

                return Result(resp.status, data)

            if not 200 <= resp.status < 300:
                log.error('Request at endpoint "{endpoint}" returned non 2xx error code {status}',
                          endpoint=endpoint,
                          status=resp.status)
            else:
                log.info('Request at endpoint "{endpoint}" returned 2xx success status code {status}',
                         endpoint=endpoint,
                         status=resp.status)

            return Result(resp.status, None)

    async def _request_or_reconnect(self, http_type: str, endpoint: str, **kwargs):

        raise_on_error = kwargs.get('raise_on_error', False)
        body = kwargs.get('data', None)
        params = kwargs.get('params', None)

        # If we are in bot_only mode stop the request and report that
        if self.bot_only:
            raise BotOnlyRequestError("Request Failed: Bot is in bot_only mode")

        # Throw if we aren't connected to notify commands or services the request failed
        if not self.connected:
            raise ApiClientRequestError('ClemBot.Api not connected')

        try:
            resp = await self._request(http_type,
                                       endpoint,
                                       raise_on_error=raise_on_error,
                                       body=body,
                                       params=params)

        # The request errored out and had raise_for_status enabled
        except aiohttp.ClientResponseError as e:
            # Check if the error was an HTTP 401 Unauthorized or HTTP 403 Forbidden,
            # this means we need to try and reconnect to the api
            # before we raise the error further
            if e.status == HTTPStatus.UNAUTHORIZED or e.status == HTTPStatus.FORBIDDEN:
                asyncio.create_task(self._disconnected())
            # Rethrow the error so it can be reported by the handlers
            raise e

        # The request failed because the Api didn't respond
        # put the client in reconnect mode and raise an error
        except aiohttp.ClientConnectorError:
            asyncio.create_task(self._disconnected())
            raise ConnectionError('Request to ClemBot.Api failed')

        # Check if the response returned an HTTP 401 Unauthorized or 403 Forbidden
        # with raise_for_status set to False We still need to handle that case
        # and put the client in reconnect mode
        if resp.status == HTTPStatus.UNAUTHORIZED or resp.status == HTTPStatus.FORBIDDEN:
            asyncio.create_task(self._disconnected())
            raise ConnectionError('Request to ClemBot.Api failed')

        return resp.value

    async def get(self, endpoint: str, **kwargs):
        """
        Sends an HTTP GET Method to ClemBot.Api

        @param endpoint: The route to make a request too
        @param kwargs:
            data: (Optional) The json request body
            raise_on_error: (Optional) (Defaults to False) Flag to tell the client to raise an exception
            for status codes above 400
        @return:
        """
        return await self._request_or_reconnect(HttpRequestType.get, endpoint, **kwargs)

    async def post(self, endpoint: str, **kwargs):
        """
        Sends an HTTP POST Method to ClemBot.Api

        @param endpoint: The route to make a request too
        @param kwargs:
            data: (Optional) The json request body
            raise_on_error: (Optional) (Defaults to False) Flag to tell the client to raise an exception
            for status codes above 400
        @return:
        """
        return await self._request_or_reconnect(HttpRequestType.post, endpoint, **kwargs)

    async def patch(self, endpoint: str, **kwargs):
        """
        Sends an HTTP PATCH Method to ClemBot.Api

        @param endpoint: The route to make a request too
        @param kwargs:
            data: (Optional) The json request body
            raise_on_error: (Optional) (Defaults to False) Flag to tell the client to raise an exception
            for status codes above 400
        @return:
        """
        return await self._request_or_reconnect(HttpRequestType.patch, endpoint, **kwargs)

    async def put(self, endpoint: str, **kwargs):
        """
        Sends an HTTP PUT Method to ClemBot.Api

        @param endpoint: The route to make a request too
        @param kwargs:
            data: (Optional) The json request body
            raise_on_error: (Optional) (Defaults to False) Flag to tell the client to raise an exception
            for status codes above 400
        @return:
        """
        return await self._request_or_reconnect(HttpRequestType.put, endpoint, **kwargs)

    async def delete(self, endpoint: str, **kwargs):
        """
        Sends an HTTP DELETE Method to ClemBot.Api

        @param endpoint: The route to make a request too
        @param kwargs:
            data: (Optional) The json request body
            raise_on_error: (Optional) (Defaults to False) Flag to tell the client to raise an exception
            for status codes above 400
        @return:
        """
        return await self._request_or_reconnect(HttpRequestType.delete, endpoint, **kwargs)
