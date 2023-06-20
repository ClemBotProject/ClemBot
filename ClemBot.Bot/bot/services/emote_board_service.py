import math

import discord
from discord import RawMessageDeleteEvent, RawMessageUpdateEvent, RawReactionActionEvent

from bot.clem_bot import ClemBot
from bot.consts import Colors, DiscordLimits
from bot.messaging.events import Events
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

        pass

    @BaseService.listener(Events.on_raw_message_edit)
    async def on_message_edit(self, event: RawMessageUpdateEvent) -> None:

        pass

    @BaseService.listener(Events.on_raw_message_delete)
    async def on_message_delete(self, event: RawMessageDeleteEvent) -> None:

        pass

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

        if len(message.content) > 0:
            for i, chunk in enumerate(self._chunk_string(message.content)):
                embed.add_field(name="Continued" if i > 0 else "Message", value=chunk, inline=False)

        if len(message.attachments) > 0:
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
                current_chunk += word[0 : starting_index]
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
