import abc

from bot.api.api_client import ApiClient


class BaseRoute(abc.ABC):

    def __init__(self, client: ApiClient):
        self._client: ApiClient = client
