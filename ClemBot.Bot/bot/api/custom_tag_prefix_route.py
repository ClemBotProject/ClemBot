import typing as t

from bot.api.api_client import ApiClient
from bot.api.base_route import BaseRoute


class CustomTagPrefixRoute(BaseRoute):
    def __init__(self, api_client: ApiClient):
        super().__init__(api_client)

    async def set_custom_tag_prefix(self, guild_id: int, tagprefix: str) -> None:
        json = {"GuildId": guild_id, "tagPrefix": tagprefix}
        await self._client.post("tags/addcustomtagprefix", data=json)

    async def remove_custom_tag_prefix(self, guild_id: int, tagprefix: str) -> None:
        json = {"GuildId": guild_id, "tagPrefix": tagprefix}
        await self._client.delete("bot/tags/deletecustomtagprefix", data=json)

    async def get_custom_tag_prefixes(self, guild_id: int, **kwargs: t.Any) -> list[str]:
        resp = await self._client.get(f"guilds/{guild_id}/customtagprefixes", **kwargs)
        return t.cast(list[str], resp["tagPrefixes"])
