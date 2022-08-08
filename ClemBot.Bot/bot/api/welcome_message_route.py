import typing as t

from bot.api.api_client import ApiClient
from bot.api.base_route import BaseRoute


class WelcomeMessageRoute(BaseRoute):
    def __init__(self, api_client: ApiClient):
        super().__init__(api_client)

    async def set_welcome_message(self, guild_id: int, message: str | None, **kwargs: t.Any) -> None:
        json = {"Message": message}
        await self._client.post(f"guilds/{guild_id}/SetWelcomeMessage", data=json, **kwargs)

    async def get_welcome_message(self, guild_id: int) -> str:
        resp = await self._client.get(f"guilds/{guild_id}/GetWelcomeMessage")
        return t.cast(str, resp["message"])

    async def delete_welcome_message(self, guild_id: int, **kwargs: t.Any) -> None:
        await self._client.delete(f"bot/guilds/{guild_id}/GetWelcomeMessage", **kwargs)
