import typing as t

from bot.api.api_client import ApiClient
from bot.api.base_route import BaseRoute
from bot.models.thread_models import Thread


class ThreadRoute(BaseRoute):
    def __init__(self, api_client: ApiClient):
        super().__init__(api_client)

    async def create_thread(
        self, thread_id: int, name: str, guild_id: int, parent_id: int, **kwargs: t.Any
    ) -> None:
        json = {"Id": thread_id, "Name": name, "GuildId": guild_id, "ParentId": parent_id}
        await self._client.post("bot/threads", data=json, **kwargs)

    async def get_thread(self, thread_id: int) -> Thread | None:
        resp = await self._client.get(f"bot/threads/{thread_id}")

        if not resp:
            return None

        return Thread(**resp)

    async def edit_thread(self, thread_id: int, name: str, **kwargs: t.Any) -> None:
        json = {
            "Id": thread_id,
            "Name": name,
        }

        await self._client.patch("bot/threads", data=json, **kwargs)

    async def remove_thread(self, thread_id: int, **kwargs: t.Any) -> None:
        await self._client.delete(f"bot/threads/{thread_id}", **kwargs)

    async def get_guilds_threads(self, guild_id: int) -> list[int] | None:
        return t.cast(list[int] | None, await self._client.get(f"bot/guilds/{guild_id}/threads"))
