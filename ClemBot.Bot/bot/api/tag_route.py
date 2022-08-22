import typing as t

import bot.models.tag_models as models
from bot.api.api_client import ApiClient
from bot.api.base_route import BaseRoute


class TagRoute(BaseRoute):
    def __init__(self, api_client: ApiClient):
        super().__init__(api_client)

    async def create_tag(
        self, name: str, content: str, guild_id: int, user_id: int, **kwargs: t.Any
    ) -> models.Tag | None:
        json = {
            "Name": name,
            "Content": content,
            "GuildId": guild_id,
            "UserId": user_id,
        }

        tag_dict = await self._client.post("tags", data=json, **kwargs)

        if not tag_dict:
            return None

        return models.Tag(**tag_dict)

    async def edit_tag_content(
        self, guild_id: int, name: str, content: str, **kwargs: t.Any
    ) -> models.Tag | None:
        json = {"GuildId": guild_id, "Name": name, "Content": content}

        tag_dict = await self._client.patch("bot/tags", data=json, **kwargs)

        if not tag_dict:
            return None

        return models.Tag(**tag_dict)

    async def edit_tag_owner(
        self, guild_id: int, name: str, user_id: int, **kwargs: t.Any
    ) -> models.Tag | None:
        json = {"GuildId": guild_id, "Name": name, "UserId": user_id}

        tag_dict = await self._client.patch("bot/tags", data=json, **kwargs)

        if not tag_dict:
            return None

        return models.Tag(**tag_dict)

    async def get_tag(self, guild_id: int, name: str, *, do_fuzzy: bool = False) -> models.Tag | None:
        json = {
            "GuildId": guild_id,
            "Name": name,
            "DoFuzzy": do_fuzzy,
        }

        tag_dict = await self._client.get("bot/tags", data=json)

        if not tag_dict:
            return None

        return models.Tag(**tag_dict)

    async def get_tag_content(self, guild_id: int, name: str) -> str | None:
        json = {
            "GuildId": guild_id,
            "Name": name,
        }

        resp = await self._client.get("bot/tags", data=json)

        return None if resp is None else resp["content"]

    async def delete_tag(
        self, guild_id: int, name: str, **kwargs: t.Any
    ) -> models.TagDelete | None:
        """
        Makes a call to the API to delete a tag w/ the given GuildId and Name.
        If successful, the API will return a dict with the given values:
        - name      The name of the tag.
        - content   The content of the tag.
        - guildId   The guild id the tag was in.
        """

        json = {
            "GuildId": guild_id,
            "Name": name,
        }

        resp = await self._client.delete("bot/tags", data=json, **kwargs)

        if not resp:
            return None

        return models.TagDelete(**resp)

    async def add_tag_use(
        self, guild_id: int, name: str, channel_id: int, user_id: int
    ) -> models.TagInvoke | None:
        """
        Makes a call to the API to say a tag w/ the given Name was used.
        If successful, the API will return a dict with the given values:
        - name      The name of the tag.
        - guildId   The guild id the tag is in.
        """
        json = {"GuildId": guild_id, "Name": name, "ChannelId": channel_id, "UserId": user_id}

        resp = await self._client.post("bot/tags/invoke", data=json)

        if not resp:
            return None

        return models.TagInvoke(**resp)

    async def get_guilds_tags(self, guild_id: int) -> list[models.Tag]:
        resp = await self._client.get(f"guilds/{guild_id}/tags")

        if not resp:
            return []

        return [models.Tag(**i) for i in resp["tags"]]

    async def search_tags(self, guild_id: int, query: str, limit: int = 5) -> list[models.Tag]:
        resp = await self._client.get(
            "bot/tags/search", data={"query": query, "guildId": guild_id, "limit": limit}
        )

        if not resp:
            return []

        return [models.Tag(**i) for i in resp["tags"]]
