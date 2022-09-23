import typing as t

from bot.api.api_client import ApiClient
from bot.api.base_route import BaseRoute
from bot.models.command_models import CommandModel, CommandStatusModel


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
    ) -> CommandStatusModel | None:

        resp = await self._client.get(
            f"bot/commands/status/{guild_id}/{channel_id}/{command_name}", **kwargs
        )

        if not resp:
            return None

        return CommandStatusModel(**resp)

    async def get_details(
        self, guild_id: int, channel_id: int, command_name: str, **kwargs: t.Any
    ) -> CommandModel | None:

        json = {"CommandName": command_name, "GuildId": guild_id, "ChannelId": channel_id}

        resp = await self._client.get("bot/commands/details", data=json, **kwargs)

        if not resp:
            return None

        return CommandModel(**resp)

    async def disable_command(
        self,
        name: str,
        guild_id: int,
        channel_id: t.Optional[int] = None,
        silent: bool = False,
        **kwargs: t.Any,
    ) -> None:

        json = {"CommandName": name, "GuildId": guild_id, "SilentlyFail": silent}
        if channel_id:
            json["ChannelId"] = channel_id

        await self._client.put("bot/commands/disable", data=json, **kwargs)

    async def enable_command(
        self, name: str, guild_id: int, channel_id: t.Optional[int] = None, **kwargs: t.Any
    ) -> None:

        json = {"CommandName": name, "GuildId": guild_id}
        if channel_id:
            json["ChannelId"] = channel_id

        await self._client.delete("bot/commands/enable", data=json, **kwargs)
