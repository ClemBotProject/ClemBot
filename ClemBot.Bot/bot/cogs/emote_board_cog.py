from typing import Union

import discord
import discord.ext.commands as commands

import bot.extensions as ext
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
            pages = self._chunked_boards(emote_boards, 16, ctx, ':placard: Emote Boards')
            await self.bot.messenger.publish(
                Events.on_set_pageable_embed, pages=pages, author=ctx.author, channel=ctx.channel
            )
            return
        if not (board := await self._get_board(emoteboard, ctx)):
            return

        pass

    async def _get_board(self, emoteboard: EMOTEBOARD_TYPE, ctx: ext.ClemBotCtx) -> EmoteBoard | None:
        """
        Gets the emote board with the following name or emote that belongs to the guild.
        Checks against both the emote board name and emote for consistency.
        Returns None if a board with the given name or emote does not exist in the guild.
        """
        value = (emoteboard if isinstance(emoteboard, str) else str(emoteboard)).casefold()
        for board in await self.bot.emote_board_route.get_emote_boards(ctx.guild):
            if board.name.casefold() == value or board.emote.casefold() == value:
                return board
        embed = discord.Embed(title=':placard: Emote Board', color=Colors.Error)
        embed.description = f'An emote board with the given {"name" if isinstance(emoteboard, str) else "emote"} ' \
                            f'{f"`{emoteboard}`" if isinstance(emoteboard, str) else emoteboard} could not be found.'
        embed.set_footer(text=str(ctx.author), icon_url=ctx.author.display_avatar.url)
        message = await ctx.send(embed=embed)
        await self.bot.messenger.publish(Events.on_set_deletable, message=message, author=ctx.author, timeout=60)
        return None

    def _chunked_boards(self, boards: list[EmoteBoard], n: int, ctx: ext.ClemBotCtx, title: str) -> list[discord.Embed]:
        """Chunks the given boards into a markdown-ed list of n-sized items (row * col)"""
        pages = []
        for chunk in chunk_sequence(boards, n):
            embed = discord.Embed(color=Colors.ClemsonOrange, title=title)
            embed.description = f'Here are the emote boards for **{ctx.guild.name}**.'
            icon_url = ctx.guild.icon.url if ctx.guild.icon else None
            embed.set_footer(text=f'{ctx.guild.name} - Emote Boards', icon_url=icon_url)
            for board in chunk:
                embed.add_field(name=board.name, value=board.emote)
            pages.append(embed)

        return pages
