from typing import Any, Union

import discord

from bot.api.api_client import ApiClient
from bot.api.base_route import BaseRoute
from bot.models.emote_board_models import (
    EmoteBoard,
    EmoteBoardPost,
    EmoteBoardReaction,
    PopularLeaderboardSlot,
    PostLeaderboardSlot,
    ReactionLeaderboardSlot,
)
from bot.utils.logging_utils import get_logger

MIN_LIMIT = 1
MAX_LIMIT = 50

log = get_logger(__name__)


class EmoteBoardRoute(BaseRoute):
    def __init__(self, client: ApiClient):
        super().__init__(client)

    async def get_emote_boards(
        self, guild: Union[int, discord.Guild], **kwargs: Any
    ) -> dict[str, str]:
        """
        Returns the emote boards in the given guild as a dictionary
        with the first element being the name of the emote board
        and the second element being the emote of the board.
        """
        guild_id = guild if isinstance(guild, int) else guild.id

        resp = await self._client.get(f"bot/emoteboards/{guild_id}", **kwargs)

        if not resp:
            return {}

        return resp

    async def get_emote_board(
        self, guild: Union[int, discord.Guild], name: str, **kwargs
    ) -> EmoteBoard | None:
        guild_id = guild if isinstance(guild, int) else guild.id

        resp = await self._client.get(f"bot/emoteboards/{guild_id}/{name}", **kwargs)

        if not resp:
            return None

        return EmoteBoard(**resp)

    async def create_emote_board(
        self, guild: Union[int, discord.Guild], board: EmoteBoard, **kwargs: Any
    ) -> None:
        data = {
            "GuildId": guild if isinstance(guild, int) else guild.id,
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

    async def edit_emote_board(
        self, guild: Union[int, discord.Guild], board: EmoteBoard, **kwargs: Any
    ) -> None:
        data = {
            "GuildId": guild if isinstance(guild, int) else guild.id,
            "Name": board.name,
            "Emote": board.emote,
            "ReactionThreshold": board.reaction_threshold,
            "AllowBotPosts": board.allow_bot_posts,
            "Channels": board.channels,
        }

        await self._client.patch("bot/emoteboards/edit", data=data, **kwargs)

    async def create_post(
        self, guild: Union[int, discord.Guild], post: EmoteBoardPost, **kwargs
    ) -> None:
        data = {
            "GuildId": guild if isinstance(guild, int) else guild.id,
            "Name": post.name,
            "ChannelId": post.channel_id,
            "MessageId": post.message_id,
            "UserId": post.user_id,
            "Reactions": post.reactions,
            "ChannelMessageIds": post.channel_message_ids,
        }

        await self._client.post("bot/emoteboardposts/create", data=data, **kwargs)

    async def get_post(
        self,
        guild: Union[int, discord.Guild],
        message: Union[int, discord.Message],
        board: Union[str, EmoteBoard, None] = None,
        **kwargs,
    ) -> list[EmoteBoardPost]:
        guild_id = guild if isinstance(guild, int) else guild.id
        message_id = message if isinstance(message, int) else message.id
        board_name: str | None = None
        if board:
            board_name = board if isinstance(board, str) else board.name

        url = f"bot/emoteboardposts/{guild_id}/"
        url += f"{board_name}/{message_id}/details" if board_name else f"{message_id}/details"

        resp = await self._client.get(url, **kwargs)

        if not resp:
            return []

        return [EmoteBoardPost(**d) for d in resp]

    async def delete_post(
        self, guild: Union[int, discord.Guild], message: Union[int, discord.Message], **kwargs
    ) -> None:
        data = {
            "GuildId": guild if isinstance(guild, int) else guild.id,
            "MessageId": message if isinstance(message, int) else message.id,
        }

        await self._client.delete("bot/emoteboardposts/delete", data=data, **kwargs)

    async def post_reactions(
        self,
        guild: Union[int, discord.Guild],
        board: Union[str, EmoteBoard],
        message: Union[int, discord.Message],
        reactions: list[int | discord.User | discord.Member],
        **kwargs,
    ) -> EmoteBoardReaction:
        data = {
            "GuildId": guild if isinstance(guild, int) else guild.id,
            "Name": board if isinstance(board, str) else board.name,
            "MessageId": message if isinstance(message, int) else message.id,
            "UserReactions": [r if isinstance(r, int) else r.id for r in reactions],
        }

        resp = await self._client.patch("bot/emoteboardposts/react", data=data, **kwargs)

        if not resp:
            return EmoteBoardReaction(update=False)

        return EmoteBoardReaction(**resp)

    async def get_popular_leaderboard(
        self,
        guild: Union[int, discord.Guild],
        board: Union[str, EmoteBoard, None] = None,
        *,
        limit: int = 5,
        **kwargs,
    ) -> list[PopularLeaderboardSlot]:
        limit = max(min(MAX_LIMIT, limit), MIN_LIMIT)
        guild_id = guild if isinstance(guild, int) else guild.id
        board_name: str | None = None
        if board:
            board_name = board if isinstance(board, str) else board.name

        url = f"bot/emoteboardposts/leaderboard/{guild_id}/"
        url += f"{board_name}/popular" if board_name else "popular"
        params = {"Limit": limit}
        resp = await self._client.get(url, params=params, **kwargs)

        if not resp:
            return []

        return [PopularLeaderboardSlot(**d) for d in resp]

    async def get_posts_leaderboard(
        self,
        guild: Union[int, discord.Guild],
        board: Union[str, EmoteBoard, None] = None,
        *,
        limit: int = 5,
        **kwargs,
    ) -> list[PostLeaderboardSlot]:
        limit = max(min(MAX_LIMIT, limit), MIN_LIMIT)
        guild_id = guild if isinstance(guild, int) else guild.id
        board_name: str | None = None

        if board:
            board_name = board if isinstance(board, str) else board.name

        url = f"bot/emoteboardposts/leaderboard/{guild_id}/"
        url += f"{board_name}/posts" if board_name else "posts"
        params = {"Limit": limit}
        resp = await self._client.get(url, params=params, **kwargs)

        if not resp:
            return []

        return [PostLeaderboardSlot(**d) for d in resp]

    async def get_reaction_leaderboard(
        self,
        guild: Union[int, discord.Guild],
        board: Union[str, EmoteBoard, None] = None,
        *,
        limit: int = 5,
        **kwargs,
    ) -> list[ReactionLeaderboardSlot]:
        limit = max(min(MAX_LIMIT, limit), MIN_LIMIT)
        guild_id = guild if isinstance(guild, int) else guild.id
        board_name: str | None = None

        if board:
            board_name = board if isinstance(board, str) else board.name

        url = f"bot/emoteboardposts/leaderboard/{guild_id}/"
        url += f"{board_name}/reactions" if board_name else "reactions"
        params = {"Limit": limit}
        resp = await self._client.get(url, params=params, **kwargs)

        if not resp:
            return []

        return [ReactionLeaderboardSlot(**d) for d in resp]
