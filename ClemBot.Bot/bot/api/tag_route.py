import typing as t

from bot.api.api_client import ApiClient
from bot.api.base_route import BaseRoute


class TagRoute(BaseRoute):

    def __init__(self, api_client: ApiClient):
        super().__init__(api_client)

    async def create_tag(self, name: str, content: str, guild_id: int, user_id: int, **kwargs):
        json = {
            'Name': name,
            'Content': content,
            'GuildId': guild_id,
            'UserId': user_id,
        }
        await self._client.post('tags', data=json, **kwargs)

    async def edit_tag(self, guild_id: int, name: str, content: str, **kwargs):
        json = {
            'GuildId': guild_id,
            'Name': name,
            'Content': content
        }
        await self._client.patch('tags', data=json, **kwargs)

    async def get_tag(self, guild_id: int, name: str):
        json = {
            'GuildId': guild_id,
            'Name': name,
        }
        return await self._client.get('tags', data=json)

    async def get_tag_content(self, guild_id: int, name: str):
        json = {
            'GuildId': guild_id,
            'Name': name,
        }

        resp = await self._client.get('tags', data=json)

        if not resp:
            return

        return resp['content']

    async def delete_tag(self, guild_id: int, name: str, **kwargs):
        json = {
            'GuildId': guild_id,
            'Name': name,
        }
        await self._client.delete('tags', data=json, **kwargs)

    async def add_tag_use(self, guild_id: int, name: str, channel_id: int, user_id: int):
        json = {
            'GuildId': guild_id,
            'Name': name,
            'ChannelId': channel_id,
            'UserId': user_id
        }

        await self._client.post('tags/invoke', data=json)

    async def get_guilds_tags(self, guild_id: int) -> t.Optional[t.List[int]]:
        return await self._client.get(f'guilds/{guild_id}/tags')
