import typing as t

from bot.api.api_client import ApiClient
from bot.api.base_route import BaseRoute
from bot.models.command_models import CommandModel


class CommandsRoute(BaseRoute):
    def __init__(self, api_client: ApiClient):
        super().__init__(api_client)

    async def add_command_invocation(
        self, command: str, guild_id: int, channel_id: int, user_id: int, **kwargs: t.Any
    ) -> None:

        json = {
            "CommandName": command,
            "GuildId": guild_id,
            "ChannelId": channel_id,
            "UserId": user_id,
        }

        await self._client.post("bot/commands", data=json, **kwargs)

    async def get_status(
        self, guild_id: int, channel_id: int, command_name: str, **kwargs: t.Any
    ) -> tuple[bool, bool]:
        resp = await self._client.get(f"bot/commands/{guild_id}/{channel_id}/{command_name}/status", **kwargs)

        if not resp:
            return False, False

        return bool(resp["disabled"]), bool(resp["silentlyFail"])

    async def get_details(
        self, guild_id: int, channel_id: int, command_name: str, **kwargs: t.Any
    ) -> CommandModel | None:
        resp = await self._client.get(
            f"bot/commands/{guild_id}/{channel_id}/{command_name}/details", **kwargs
        )

        if not resp:
            return None

        return CommandModel(**resp)

    async def enable_command(
            self, name: str, guild_id: int, channel_id: t.Optional[int] = None, silent: bool = False, **kwargs: t.Any
    ) -> None:
        json = {

        }
        pass

    async def disable_command(self) -> None:
        pass
