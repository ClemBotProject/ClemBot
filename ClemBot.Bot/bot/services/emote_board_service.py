import math
from typing import Union

import discord
from discord import (
    NotFound,
    RawMessageDeleteEvent,
    RawMessageUpdateEvent,
    RawReactionActionEvent,
    Reaction,
)

from bot.clem_bot import ClemBot
from bot.consts import Colors, DiscordLimits
from bot.messaging.events import Events
from bot.models.emote_board_models import EmoteBoard, EmoteBoardPost
from bot.services.base_service import BaseService
from bot.utils.logging_utils import get_logger

log = get_logger(__name__)

RANKINGS = [
    "POPULAR",
    "QUALITY",
    "*THE PEOPLE HAVE SPOKEN*",
    "*INCREDIBLE*",
    "**LEGENDARY**",
    "***GOD-TIER***",
]


class EmoteBoardService(BaseService):
    """
    The service that manages reactions, message edits, and message deletions for emote boards and posts.

    This service uses the raw version of events to bypass automatic filtering of events.
    For example, `Events.on_message_delete` will not be dispatched if the message's author is the bot.
    This behavior is perfectly fine for most services but can cause unexpected behavior for this feature,
    due to the optional configuration of allowing bot messages to be posted to an emote board.
    """

    def __init__(self, bot: ClemBot):
        super().__init__(bot)

    @BaseService.listener(Events.on_raw_reaction_add)
    async def on_reaction_add(self, event: RawReactionActionEvent) -> None:
        if not event.guild_id:
            return

        if not (board := await self._get_board_from_emote(event.guild_id, event.emoji)):
            return

        # ignore if the emote board has no channels
        if not board.channels:
            return

        guild = self.bot.get_guild(event.guild_id)
        assert guild is not None

        channel = guild.get_channel_or_thread(event.channel_id)
        assert channel is not None

        if not isinstance(channel, discord.abc.MessageableChannel):
            return

        message = await channel.fetch_message(event.message_id)

        # ignore if the author is a bot and the board does NOT allow bot posts
        if message.author.bot and not board.allow_bot_posts:
            return

        reaction: Reaction | None = None

        for r in message.reactions:
            if str(r.emoji) == str(event.emoji):
                reaction = r
                break

        # if this is None, something is VERY wrong.
        assert reaction is not None

        users = [u async for u in reaction.users() if u != message.author]

        # ignore if the num. of valid users does not reach the threshold
        if len(users) < board.reaction_threshold:
            return

        post = await self.bot.emote_board_route.get_post_from_board(guild, message, board)

        # if the user is a bot, it's very likely we did not store their message in the db...
        if message.author.bot:
            stored_message = await self.bot.message_route.get_message(message.id)
            if stored_message is None:
                await self.bot.message_route.create_message(
                    message.id,
                    message.content,
                    guild.id,
                    message.author.id,
                    channel.id,
                    message.created_at,
                    raise_on_error=True,
                )

        if not post:
            await self._create_post(board, message, users)
            return

        if not post.count_reaction(event.user_id):
            return

        await self._update_post(board, post, message, users)

    @BaseService.listener(Events.on_raw_message_edit)
    async def on_message_edit(self, event: RawMessageUpdateEvent) -> None:
        if not event.guild_id:
            return

        guild = self.bot.get_guild(event.guild_id)
        assert guild is not None

        channel = guild.get_channel_or_thread(event.channel_id)
        assert channel is not None and isinstance(channel, discord.abc.Messageable)

        # Attempt to fetch the message, ignore if we do not have permissions.
        message: discord.Message
        try:
            message = await channel.fetch_message(event.message_id)
        except discord.Forbidden:
            log.info(
                "Fetching message {message_id} from channel {channel_id} in guild {guild_id} raised Forbidden on_message_edit",
                message_id=event.message_id,
                channel_id=event.channel_id,
                guild_id=event.guild_id,
            )
            return

        posts = await self.bot.emote_board_route.get_posts(event.guild_id, event.message_id)

        post_boards: list[tuple[EmoteBoardPost, EmoteBoard]] = []

        for post in posts:
            board = await self.bot.emote_board_route.get_emote_board(
                guild, post.name, raise_on_error=True
            )
            if not board:
                log.warning(
                    "Fetching board via post linking to board {board} returned None",
                    board=post.name,
                )
                continue
            post_boards.append((post, board))

        for post, emote_board in post_boards:
            for channel_id, message_id in post.channel_message_ids.items():
                try:
                    if not (channel := guild.get_channel_or_thread(channel_id)):
                        continue

                    assert isinstance(channel, discord.abc.Messageable)
                    embed_msg = await channel.fetch_message(message_id)
                    embed = await self._as_embed(
                        message,
                        emote_board.reaction_threshold,
                        len(post.reactions),
                        emote_board.emote,
                    )
                    await embed_msg.edit(embed=embed)
                except NotFound:  # Skips over the item if fetch_message() raises `NotFound`
                    continue

    @BaseService.listener(Events.on_raw_message_delete)
    async def on_message_delete(self, event: RawMessageDeleteEvent) -> None:
        if not event.guild_id:
            return

        guild = self.bot.get_guild(event.guild_id)
        assert guild is not None

        posts = await self.bot.emote_board_route.get_posts(event.guild_id, event.message_id)

        for post in posts:
            for channel_id, message_id in post.channel_message_ids.items():
                try:
                    if not (channel := guild.get_channel_or_thread(channel_id)):
                        continue

                    assert isinstance(channel, discord.abc.Messageable)
                    embed_msg = await channel.fetch_message(message_id)
                    await embed_msg.delete()
                except NotFound:  # Skips over the item if fetch_message() raises `NotFound`
                    continue

    async def _create_post(
        self,
        board: EmoteBoard,
        message: discord.Message,
        users: list[discord.User | discord.Member] | list[int],
    ) -> None:
        """
        Creates an EmoteBoardPost and sends embed(s) to the channel(s) the EmoteBoard is subbed to.
        Sends the post information to the API.
        This method does not do any preliminary checks and assumes the given params meet the reqs.
        """
        post = EmoteBoardPost(
            name=board.name,
            channel_id=message.channel.id,
            message_id=message.id,
            user_id=message.author.id,
            channel_message_ids={},
            reactions=[u if isinstance(u, int) else u.id for u in users],
        )

        guild = message.guild
        assert guild is not None

        embed = await self._as_embed(
            message, board.reaction_threshold, len(post.reactions), board.emote
        )

        for channel_id in board.channels:
            if not (channel := guild.get_channel_or_thread(channel_id)):
                continue
            assert isinstance(channel, discord.abc.Messageable)
            message = await channel.send(embed=embed)
            post.channel_message_ids[channel_id] = message.id

        await self.bot.emote_board_route.create_post(guild, post, raise_on_error=True)

    async def _update_post(
        self,
        board: EmoteBoard,
        post: EmoteBoardPost,
        message: discord.Message,
        users: list[discord.User | discord.Member] | list[int],
    ) -> None:
        """
        Attempts to update the given `post` that belongs to the given `board`.
        Checks against the API to verify an update is necessary before updating any messages.
        This method does not do any preliminary checks and assumes the given params meet the reqs.
        """
        guild = message.guild
        assert guild is not None

        reaction_dto = await self.bot.emote_board_route.post_reactions(guild, board, message, users)

        if not reaction_dto.update or reaction_dto.reaction_count is None:
            return

        embed = await self._as_embed(
            message, board.reaction_threshold, reaction_dto.reaction_count, board.emote
        )

        for channel_id, message_id in post.channel_message_ids.items():
            try:
                if not (channel := guild.get_channel_or_thread(channel_id)):
                    continue

                if not isinstance(channel, discord.abc.Messageable):
                    continue

                embed_msg = await channel.fetch_message(message_id)
                await embed_msg.edit(embed=embed)
            except discord.NotFound:
                continue

    async def _get_board_from_emote(
        self,
        guild: Union[int, discord.Guild],
        emote: Union[str, discord.PartialEmoji, discord.Emoji],
    ) -> EmoteBoard | None:
        """
        Fetches the EmoteBoard from the given `guild` with the corresponding `emote`.
        If no board has the given `emote`, None is returned.
        """
        boards = await self.bot.emote_board_route.get_emote_boards(guild)
        emote_str = emote if isinstance(emote, str) else str(emote)

        for name, board_emote in boards.items():
            if emote_str == board_emote:
                return await self.bot.emote_board_route.get_emote_board(
                    guild, name, raise_on_error=True
                )

        return None

    async def _as_embed(
        self, message: discord.Message, threshold: int, reactions: int, emote: str
    ) -> discord.Embed:
        """
        Transforms the given message into an embed meant to be sent to an emote board's channels.
        """
        multiplier = min(math.floor((reactions - threshold) / threshold), len(RANKINGS) - 1)
        title = f"{emote} {RANKINGS[multiplier]} | {reactions} {emote}"
        assert isinstance(
            message.channel,
            discord.TextChannel | discord.VoiceChannel | discord.StageChannel | discord.Thread,
        )

        embed = discord.Embed(
            title=title,
            color=Colors.ClemsonOrange,
            description=f"_Posted in {message.channel.mention} by_ {message.author.mention}",
        )

        embed.add_field(name="Original Message", value=message.jump_url)

        if message.content:
            for i, chunk in enumerate(self._chunk_string(message.content)):
                embed.add_field(name="Continued" if i > 0 else "Message", value=chunk, inline=False)

        if message.attachments:
            for attachment in message.attachments:
                if not attachment.content_type:
                    continue
                if attachment.content_type.startswith("image"):
                    embed.set_image(url=attachment.url)
                    break

        embed.set_thumbnail(url=message.author.display_avatar.url)
        embed.set_footer(text=f"Sent on {message.created_at.strftime('%m/%d/%Y')}")

        return embed

    def _chunk_string(
        self, string: str, chunk_size: int = DiscordLimits.EmbedFieldLength
    ) -> list[str]:
        """
        Chunks the given string into substrings of max size `chunk_size`.
        Splits at whitespace if possible, otherwise splits at the chunk size.
        """
        if len(string) <= chunk_size:
            return [string]

        chunks = [""]
        for word in iter(string.split()):
            current_chunk: str = chunks[-1]

            # check to see if we cannot fit the word at the end of our current chunk
            # if so, create a new chunk and reassign `current_chunk`
            if len(current_chunk) + len(word) > chunk_size and len(current_chunk) > 0:
                chunks.append("")
                current_chunk = ""

            # check to see if our current word is larger than the chunk size
            # if so, break up the "word" into `chunk_size` bites.
            if len(word) > chunk_size:

                # append as much of our `word` as we can to the current chunk
                # and replace the last element in `chunks`
                starting_index = chunk_size - len(current_chunk)
                current_chunk += word[0:starting_index]
                chunks[-1] = current_chunk

                # start from where we left off for the previous chunk
                # split and append to `chunks` based on `chunk_size`
                for i in range(starting_index, len(word), chunk_size):
                    chunks.append(word[i : i + chunk_size])

                chunks[-1] += " "

            # this word can fit at the end of the current chunk
            # without going over the given `chunk_size`
            else:
                current_chunk += word + " "
                if current_chunk.strip():
                    chunks[-1] = current_chunk

        return chunks

    async def load_service(self) -> None:
        pass
