from bot.api.api_client import ApiClient
from bot.api.base_route import BaseRoute

import typing as t
from bot.models import Tag


class TagRoute(BaseRoute):

    def __init__(self, api_client: ApiClient):
        super().__init__(api_client)

    async def create_tag(self, name: str, content: str, guild_id: int, user_id: int, **kwargs) -> t.Optional[Tag]:
        json = {
            'Name': name,
            'Content': content,
            'GuildId': guild_id,
            'UserId': user_id,
        }
        tag_dict = await self._client.post('tags', data=json, **kwargs)
        if not tag_dict:
            return None
        return Tag.from_dict(tag_dict)

    async def edit_tag_content(self, guild_id: int, name: str, content: str, **kwargs) -> t.Optional[Tag]:
        json = {
            'GuildId': guild_id,
            'Name': name,
            'Content': content
        }
        tag_dict = await self._client.patch('bot/tags', data=json, **kwargs)
        if not tag_dict:
            return None
        return Tag.from_dict(tag_dict)

    async def edit_tag_owner(self, guild_id: int, name: str, user_id: int, **kwargs) -> t.Optional[Tag]:
        json = {
            'GuildId': guild_id,
            'Name': name,
            'UserId': user_id
        }
        tag_dict = await self._client.patch('bot/tags', data=json, **kwargs)
        if not tag_dict:
            return None
        return Tag.from_dict(tag_dict)

    async def get_tag(self, guild_id: int, name: str) -> t.Optional[Tag]:
        json = {
            'GuildId': guild_id,
            'Name': name,
        }
        tag_dict = await self._client.get('bot/tags', data=json)
        if not tag_dict:
            return None
        return Tag.from_dict(tag_dict)

    async def get_tag_content(self, guild_id: int, name: str) -> t.Optional[str]:
        json = {
            'GuildId': guild_id,
            'Name': name,
        }
        resp = await self._client.get('bot/tags', data=json)
        return None if resp is None else resp['content']

    async def delete_tag(self, guild_id: int, name: str, **kwargs):
        """
        Makes a call to the API to delete a tag w/ the given GuildId and Name.
        If successful, the API will return a dict with the given values:
        - name      The name of the tag.
        - content   The content of the tag.
        - guildId   The guild id the tag was in.
        """
        json = {
            'GuildId': guild_id,
            'Name': name,
        }
        return await self._client.delete('bot/tags', data=json, **kwargs)

    async def add_tag_use(self, guild_id: int, name: str, channel_id: int, user_id: int):
        """
        Makes a call to the API to say a tag w/ the given Name was used.
        If successful, the API will return a dict with the given values:
        - name      The name of the tag.
        - guildId   The guild id the tag is in.
        """
        json = {
            'GuildId': guild_id,
            'Name': name,
            'ChannelId': channel_id,
            'UserId': user_id
        }

        return await self._client.post('bot/tags/invoke', data=json)

    async def get_guilds_tags(self, guild_id: int) -> t.Iterator[Tag]:
        resp = await self._client.get(f'guilds/{guild_id}/tags')

        if not resp:
            return []

        return [Tag.from_dict(i) for i in resp['tags']]
