from typing import Union

import discord
import discord.ext.commands as commands

import bot.extensions as ext
from bot import bot_secrets
from bot.clem_bot import ClemBot
from bot.consts import Colors
from bot.messaging.events import Events
from bot.models.emote_board_models import EmoteBoard
from bot.utils.helpers import chunk_sequence

EMOTEBOARD_TYPE = Union[str, discord.PartialEmoji]


class EmoteBoardCog(commands.Cog):
    def __init__(self, bot: ClemBot):
        self.bot = bot

    @ext.group(case_insensitive=True, invoke_without_command=True, aliases=['starboard', 'eb', 'sb', 'board'])
    @ext.long_help('Add, remove, edit, list, and view the leaderboard for emote board posts.')
    @ext.short_help('List the emote boards in the server.')
    async def emoteboard(self, ctx: ext.ClemBotCtx, emoteboard: EMOTEBOARD_TYPE | None = None) -> None:
        emote_boards = await self.bot.emote_board_route.get_emote_boards(ctx.guild)
        if not emoteboard and not len(emote_boards):
            embed = discord.Embed(title=':placard: Emote Boards', color=Colors.ClemsonOrange)
            embed.description = 'There are no emote boards for this server.'
            await ctx.send(embed=embed)
            return
        elif not emoteboard:
            pages = self.chunked_boards(emote_boards, 16, ctx, ':placard: Emote Boards')
            await self.bot.messenger.publish(
                Events.on_set_pageable_embed, pages=pages, author=ctx.author, channel=ctx.channel
            )
            return

        pass

    def chunked_boards(self, boards: list[EmoteBoard], n: int, ctx: ext.ClemBotCtx, title: str) -> list[discord.Embed]:
        """Chunks the given boards into a markdown-ed list of n-sized items (row * col)"""
        pages = []
        for chunk in chunk_sequence(boards, n):
            embed = discord.Embed(color=Colors.ClemsonOrange, title=title)
            embed.description = 'Here are the emote boards for this server.'
            embed.set_footer(text=f'{ctx.guild.name} - Emote Boards', icon_url=ctx.guild.icon.url)
            for board in chunk:
                embed.add_field(name=board.name, value=board.emote)
            pages.append(embed)

        return pages
