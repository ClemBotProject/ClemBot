import typing as t

from bot.api.api_client import ApiClient
from bot.api.base_route import BaseRoute


class CommandsRoute(BaseRoute):

    def __init__(self, api_client: ApiClient):
        super().__init__(api_client)

    async def add_command_invocation(self,
                                     command: str,
                                     guild_id: int,
                                     channel_id: int,
                                     user_id: int,
                                     **kwargs) -> None:

        json = {
            'CommandName': command,
            'GuildId': guild_id,
            'ChannelId': channel_id,
            'UserId': user_id
        }

        return await self._client.post('bot/commands', data=json, **kwargs)
