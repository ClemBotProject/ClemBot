from bot.api.api_client import ApiClient
from bot.api.base_route import BaseRoute


class CustomPrefixRoute(BaseRoute):

    def __init__(self, api_client: ApiClient):
        super().__init__(api_client)

    async def set_custom_prefix(self, guild_id: int, prefix: str):
        json = {
            'GuildId': guild_id,
            'Prefix': prefix
        }
        return await self._client.post('customprefixes/add', data=json)

    async def remove_custom_prefix(self, guild_id: int, prefix: str):
        json = {
            'GuildId': guild_id,
            'Prefix': prefix
        }
        return await self._client.delete('bot/customprefixes/remove', data=json)

    async def get_custom_prefixes(self, guild_id: int, **kwargs):
        resp = await self._client.get(f'guilds/{guild_id}/customprefixes', **kwargs)
        return resp['prefixes']
