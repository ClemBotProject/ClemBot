import typing as t

from bot.api.api_client import ApiClient
from bot.api.base_route import BaseRoute


class ChannelRoute(BaseRoute):

    def __init__(self, api_client: ApiClient):
        super().__init__(api_client)

    async def create_channel(self, channel_id: int, name: int, guild_id: int, **kwargs):
        json = {
            'Id': channel_id,
            'Name': name,
            'GuildId': guild_id
        }
        await self._client.post('bot/channels', data=json, **kwargs)

    async def get_channel(self, channel_id: int):
        return await self._client.get(f'bot/channels/{channel_id}')

    async def edit_channel(self, channel_id: int, name: str, **kwargs):
        json = {
            'Id': channel_id,
            'Name': name,
        }

        return await self._client.patch('bot/channels', data=json, **kwargs)

    async def remove_channel(self, channel_id: int, **kwargs):
        return await self._client.delete(f'bot/channels/{channel_id}', **kwargs)

    async def get_guilds_channels(self, guild_id: int) -> t.Optional[t.List[int]]:
        return await self._client.get(f'bot/guilds/{guild_id}/channels')
