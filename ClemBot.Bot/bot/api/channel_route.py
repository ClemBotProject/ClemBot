import typing as t

from bot.api.api_client import ApiClient
from bot.api.base_route import BaseRoute
from bot.models.channel_models import Channel


class ChannelRoute(BaseRoute):
    def __init__(self, api_client: ApiClient):
        super().__init__(api_client)

    async def create_channel(self, channel_id: int, name: int, guild_id: int, **kwargs: t.Any) -> None:
        json = {"Id": channel_id, "Name": name, "GuildId": guild_id}
        await self._client.post("bot/channels", data=json, **kwargs)

    async def get_channel(self, channel_id: int) -> Channel:
        return Channel(**await self._client.get(f"bot/channels/{channel_id}"))

    async def edit_channel(self, channel_id: int, name: str, **kwargs: t.Any) -> None:
        json = {
            "Id": channel_id,
            "Name": name,
        }

        await self._client.patch("bot/channels", data=json, **kwargs)

    async def remove_channel(self, channel_id: int, **kwargs: t.Any) -> None:
        await self._client.delete(f"bot/channels/{channel_id}", **kwargs)

    async def get_guilds_channels(self, guild_id: int) -> t.Optional[list[int]]:
        return t.cast(t.Optional[list[int]], await self._client.get(f"bot/guilds/{guild_id}/channels"))
