from typing import Union, Any

import discord

from bot.api.api_client import ApiClient
from bot.api.base_route import BaseRoute
from bot.models.emote_board_models import EmoteBoard


class EmoteBoardRoute(BaseRoute):
    def __init__(self, client: ApiClient):
        super().__init__(client)

    async def get_emote_boards(self, guild: Union[int, discord.Guild], **kwargs: Any) -> list[EmoteBoard]:
        guild_id = guild if isinstance(guild, int) else guild.id

        resp = await self._client.get(f"bot/emoteboard/{guild_id}", **kwargs)

        if not resp:
            return []

        return [EmoteBoard(**d) for d in resp]
