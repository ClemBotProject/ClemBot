from bot.api.api_client import ApiClient
from bot.api.base_route import BaseRoute


class WelcomeMessageRoute(BaseRoute):

    def __init__(self, api_client: ApiClient):
        super().__init__(api_client)

    async def set_welcome_message(self, guild_id: int, message: str, **kwargs):
        json = {
            'Message': message
        }
        return await self._client.post(f'guilds/{guild_id}/SetWelcomeMessage', data=json, **kwargs)

    async def get_welcome_message(self, guild_id: int):
        resp = await self._client.get(f'guilds/{guild_id}/GetWelcomeMessage')
        return resp['message']

    async def delete_welcome_message(self, guild_id: int, **kwargs):
        return await self._client.delete(f'bot/guilds/{guild_id}/GetWelcomeMessage', **kwargs)
