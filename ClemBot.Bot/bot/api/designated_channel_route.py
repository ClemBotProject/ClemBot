import typing as t

from bot.api.api_client import ApiClient
from bot.api.base_route import BaseRoute


class DesignatedChannelRoute(BaseRoute):
    def __init__(self, api_client: ApiClient):
        super().__init__(api_client)

    async def register_channel(self, channel_id: int, designation: str, **kwargs: t.Any) -> None:
        json = {"ChannelId": channel_id, "Designation": designation}

        await self._client.post("bot/designatedchannels", data=json, **kwargs)

    async def delete_channel(self, channel_id: int, designation: str, **kwargs: t.Any) -> None:
        json = {"ChannelId": channel_id, "Designation": designation}

        await self._client.delete("bot/designatedchannels", data=json, **kwargs)

    async def get_guild_designated_channel_ids(self, guild_id: int, designation: str) -> list[t.Any]:
        json = {"GuildId": guild_id, "Designation": designation}
        resp = await self._client.get("bot/designatedchannels/details", data=json)

        if not resp:
            return []

        return t.cast(list[t.Any], resp["mappings"])

    async def get_guild_all_designated_channels(self, guild_id: int) -> dict[t.Any, t.Any]:
        resp = await self._client.get(f"bot/guilds/{guild_id}/designatedchannels")

        if not resp:
            return {}

        return {i["designation"]: i["channelIds"] for i in resp}

    async def get_global_designations(self, designation: str) -> t.Any:
        return await self._client.get(f"bot/designatedchannels/{designation}/index")
