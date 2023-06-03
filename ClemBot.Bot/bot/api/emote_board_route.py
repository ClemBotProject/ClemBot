import json
from typing import Any, Union

import discord

from bot.api.api_client import ApiClient
from bot.api.base_route import BaseRoute
from bot.models.emote_board_models import EmoteBoard


class EmoteBoardRoute(BaseRoute):
    def __init__(self, client: ApiClient):
        super().__init__(client)

    async def get_emote_boards(
        self, guild: Union[int, discord.Guild], **kwargs: Any
    ) -> list[EmoteBoard]:
        guild_id = guild if isinstance(guild, int) else guild.id

        resp = await self._client.get(f"bot/emoteboards/{guild_id}", **kwargs)

        if not resp:
            return []

        return [EmoteBoard(**d) for d in resp]

    async def create_emote_board(self, board: EmoteBoard, **kwargs: Any) -> None:
        data = {
            "GuildId": board.guild_id,
            "Name": board.name,
            "Emote": board.emote,
            "ReactionThreshold": board.reaction_threshold,
            "AllowBotPosts": board.allow_bot_posts,
            "Channels": board.channels,
        }

        await self._client.post("bot/emoteboards/create", data=data, **kwargs)

    async def delete_emote_board(
        self, guild: Union[int, discord.Guild], name: str, **kwargs: Any
    ) -> None:
        data = {"GuildId": guild if isinstance(guild, int) else guild.id, "Name": name}

        await self._client.delete("bot/emoteboards/delete", data=data, **kwargs)

    async def edit_emote_board(self, board: EmoteBoard, **kwargs: Any) -> None:
        data = {
            "GuildId": board.guild_id,
            "Name": board.name,
            "Emote": board.emote,
            "ReactionThreshold": board.reaction_threshold,
            "AllowBotPosts": board.allow_bot_posts,
            "Channels": board.channels,
        }

        await self._client.patch("bot/emoteboards/edit", data=data, **kwargs)
