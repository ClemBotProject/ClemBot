import typing as t
from bot.api.api_client import ApiClient
from bot.api.base_route import BaseRoute
from dataclasses import dataclass
from dataclasses_json import LetterCase, DataClassJsonMixin, dataclass_json


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class Tag(DataClassJsonMixin):
    name: str
    content: str
    creation_date: str
    guild_id: int
    user_id: int
    use_count: int


class TagRoute(BaseRoute):

    def __init__(self, api_client: ApiClient):
        super().__init__(api_client)

    async def create_tag(self, name: str, content: str, guild_id: int, user_id: int, **kwargs) -> t.Optional[Tag]:
        json = {
            'Name': name.lower(),
            'Content': content,
            'GuildId': guild_id,
            'UserId': user_id,
        }
        tag_dict = await self._client.post('tags', data=json, **kwargs)
        return None if tag_dict is None else Tag.from_dict(tag_dict)

    async def temp_edit_tag(self, guild_id: int, name: str, content: str, user_id: int) -> t.Optional[Tag]:
        # TODO: Remove before merging back into master. This is temporary.
        json = {
            'GuildId': guild_id,
            'Name': name.lower(),
            'Content': content,
            'UserId': user_id
        }
        tag_dict = await self._client.patch('tags', data=json)
        return None if tag_dict is None else Tag.from_dict(tag_dict)

    async def edit_tag_content(self, guild_id: int, name: str, content: str, **kwargs) -> t.Optional[Tag]:
        json = {
            'GuildId': guild_id,
            'Name': name.lower(),
            'Content': content
        }
        tag_dict = await self._client.patch('tags', data=json, **kwargs)
        return None if tag_dict is None else Tag.from_dict(tag_dict)

    async def edit_tag_owner(self, guild_id: int, name: str, user_id: int, **kwargs) -> t.Optional[Tag]:
        json = {
            'GuildId': guild_id,
            'Name': name.lower(),
            'UserId': user_id
        }
        tag_dict = await self._client.patch('tags', data=json, **kwargs)
        return None if tag_dict is None else Tag.from_dict(tag_dict)

    async def get_tag(self, guild_id: int, name: str) -> t.Optional[Tag]:
        json = {
            'GuildId': guild_id,
            'Name': name.lower(),
        }
        tag_dict = await self._client.get('tags', data=json)
        return None if tag_dict is None else Tag.from_dict(tag_dict)

    async def get_tag_content(self, guild_id: int, name: str) -> t.Optional[str]:
        json = {
            'GuildId': guild_id,
            'Name': name.lower(),
        }
        resp = await self._client.get('tags', data=json)
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
            'Name': name.lower(),
        }
        return await self._client.delete('tags', data=json, **kwargs)

    async def add_tag_use(self, guild_id: int, name: str, channel_id: int, user_id: int):
        """
        Makes a call to the API to say a tag w/ the given Name was used.
        If successful, the API will return a dict with the given values:
        - name      The name of the tag.
        - guildId   The guild id the tag is in.
        """
        json = {
            'GuildId': guild_id,
            'Name': name.lower(),
            'ChannelId': channel_id,
            'UserId': user_id
        }

        return await self._client.post('tags/invoke', data=json)

    async def get_guilds_tags(self, guild_id: int) -> t.Iterator[Tag]:
        resp = await self._client.get(f'guilds/{guild_id}/tags')

        if not resp:
            return []

        return [Tag.from_dict(i) for i in resp]
