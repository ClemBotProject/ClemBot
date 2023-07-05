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
    def __init__(self, bot: ClemBot):
        super().__init__(bot)

    @BaseService.listener(Events.on_raw_reaction_add)
    async def on_reaction_add(self, event: RawReactionActionEvent) -> None:
        if not (board := await self._get_board_from_emote(event.guild_id, event.emoji)):
            return

        # ignore if the emote board has no channels
        if not board.channels:
            return

        guild = self.bot.get_guild(event.guild_id)
        channel = guild.get_channel(event.channel_id)
        message = await channel.fetch_message(event.message_id)

        # ignore if the author is a bot and the board does NOT allow bot posts
        if message.author.bot and not board.allow_bot_posts:
            return

        reaction: Reaction | None = None

        for r in message.reactions:
            if r.emoji == event.emoji:
                reaction = r
                break

        # if this is None, something is VERY wrong.
        assert reaction is not None

        users = [u async for u in reaction.users() if u != message.author]

        # ignore if the num. of valid users does not reach the threshold
        if len(users) < board.reaction_threshold:
            return

        if not (post := await self.bot.emote_board_route.get_post(guild, message, board)):
            await self._create_post(board, message, users)
        else:
            await self._update_post(board, post, message, users)

    @BaseService.listener(Events.on_raw_message_edit)
    async def on_message_edit(self, event: RawMessageUpdateEvent) -> None:
        # try and rule out the message as quick as possible with the least amount of work
        if event.cached_message and not len(event.cached_message.reactions):
            return
        guild = self.bot.get_guild(event.guild_id)
        channel = guild.get_channel(event.channel_id)
        message = await channel.fetch_message(event.message_id)

        if not message.reactions:
            return

        # get the boards that correspond to each reaction on the message
        boards = await self.bot.emote_board_route.get_emote_boards(guild, raise_on_error=True)
        emotes = {str(r.emoji): r.count for r in message.reactions}
        boards_in_msg = [b for b in boards if b.emote in emotes]

        if not boards_in_msg:
            return

        posts = await self.bot.emote_board_route.get_post(guild, message)
        board_names = {b.name: b for b in boards_in_msg}
        board_posts = {board_names[post.name]: post for post in posts if post.name in board_names}

        for board, post in board_posts:
            embed = await self._as_embed(
                message, board.reaction_threshold, len(post.reactions), board.emote
            )
            for channel_id, message_id in post.channel_message_ids:
                try:
                    post_message = await guild.get_channel(channel_id).fetch_message(message_id)
                    await post_message.edit(embed=embed)
                except NotFound:
                    continue

    @BaseService.listener(Events.on_raw_message_delete)
    async def on_message_delete(self, event: RawMessageDeleteEvent) -> None:
        # try and rule out the message as quick as possible with the least amount of work
        if event.cached_message and not len(event.cached_message.reactions):
            return

        if event.cached_message:
            boards = await self.bot.emote_board_route.get_emote_boards(
                event.guild_id, raise_on_error=True
            )
            emotes = {str(r.emoji): r.count for r in event.cached_message.reactions}
            if not [b for b in boards if b.emote in emotes]:
                return

        guild = self.bot.get_guild(event.guild_id)
        posts = await self.bot.emote_board_route.get_post(event.guild_id, event.message_id)

        for post in posts:
            for channel_id, message_id in post.channel_message_ids:
                try:
                    embed_msg = await guild.get_channel(channel_id).fetch_message(message_id)
                    await embed_msg.delete()
                except NotFound:
                    continue

    async def _create_post(
        self,
        board: EmoteBoard,
        message: discord.Message,
        users: list[discord.User | discord.Member | int],
    ) -> None:
        """
        Creates an EmoteBoardPost and sends embed(s) to the channel(s) the EmoteBoard is subbed to.
        Sends the post information to the API.
        This method does not do any preliminary checks and assumes the given params meet the reqs.
        """
        post = EmoteBoardPost()
        post.name = board.name
        post.channel_id = message.channel.id
        post.message_id = message.id
        post.user_id = message.author.id
        post.channel_message_ids = {}
        post.reactions = [u if isinstance(u, int) else u.id for u in users]

        guild = message.guild
        embed = await self._as_embed(
            message, board.reaction_threshold, len(post.reactions), board.emote
        )

        for channel_id in board.channels:
            if not (channel := guild.get_channel(channel_id)):
                continue
            assert isinstance(channel, discord.TextChannel | discord.Thread)
            message = await channel.send(embed=embed)
            post.channel_message_ids[channel_id] = message.id

        await self.bot.emote_board_route.create_post(guild, post, raise_on_error=True)

    async def _update_post(
        self,
        board: EmoteBoard,
        post: EmoteBoardPost,
        message: discord.Message,
        users: list[discord.User | discord.Member | int],
    ) -> None:
        """
        Attempts to update the given `post` that belongs to the given `board`.
        Checks against the API to verify an update is necessary before updating any messages.
        This method does not do any preliminary checks and assumes the given params meet the reqs.
        """
        reaction_dto = await self.bot.emote_board_route.post_reactions(
            message.guild, board, message, users
        )

        if not reaction_dto.update:
            return

        guild = message.guild
        embed = await self._as_embed(
            message, board.reaction_threshold, reaction_dto.reactions, board.emote
        )

        for channel_id, message_id in post.channel_message_ids:
            try:
                embed_msg = await guild.get_channel(channel_id).fetch_message(message_id)
                await embed_msg.edit(embed=embed)
            except NotFound:
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

        for name, emote in boards:
            if emote_str == emote:
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
        assert isinstance(message.channel, discord.TextChannel | discord.Thread)

        embed = discord.Embed(
            title=title,
            color=Colors.ClemsonOrange,
            description=f"_Posted in {message.channel.mention} by_ {message.author.mention} [Link]({message.jump_url})",
        )

        if message.content:
            for i, chunk in enumerate(self._chunk_string(message.content)):
                embed.add_field(name="Continued" if i > 0 else "Message", value=chunk, inline=False)

        if message.attachments:
            embed.set_image(url=message.attachments[0].url)

        embed.set_thumbnail(url=message.author.display_avatar.url)
        embed.set_footer(text=f"Sent on {message.created_at.strftime('%m/%d/%Y')}")

        return embed

    def _chunk_string(
        self, string: str, chunk_size: int = DiscordLimits.EmbedFieldLength
    ) -> list[str]:
        """
        Chunks the given string into substrings of max size `chunk_size`.
        Splits at whitespace, if possible, otherwise splits at the chunk size.
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
                if len(current_chunk.strip()) > 0:
                    chunks[-1] = current_chunk

        return chunks

    async def load_service(self) -> None:
        pass
