from typing import Union

import discord
import discord.ext.commands as commands
import emoji

import bot.extensions as ext
from bot.clem_bot import ClemBot
from bot.consts import Colors, Claims
from bot.messaging.events import Events
from bot.models.emote_board_models import EmoteBoard
from bot.utils.helpers import chunk_sequence

EMOTEBOARD_TYPE = Union[str, discord.PartialEmoji]


class EmoteBoardCog(commands.Cog):
    def __init__(self, bot: ClemBot):
        self.bot = bot

    @ext.group(case_insensitive=True, invoke_without_command=True, aliases=['eb', 'board', 'boards', 'emojiboard'])
    @ext.long_help('Add, remove, edit, list, and view the leaderboard for emote board posts.')
    @ext.short_help('List the emote boards in the server.')
    @ext.example(['boards', 'board :star:', 'board starboard'])
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
        if not (board := await self._get_board(emoteboard, ctx, True)):
            return
        channel_mentions = []
        for channel_id in board.channels:
            if channel := ctx.guild.get_channel(channel_id):
                channel_mentions.append(channel.mention)
        embed = discord.Embed(title=':placard: Emote Boards', color=Colors.ClemsonOrange)
        embed.description = f'Here is the information for **{board.emote} {board.name}**'
        embed.add_field(name='Name', value=board.name)
        embed.add_field(name='Emote', value=board.emote)
        embed.add_field(name='Reaction Threshold', value=board.reaction_threshold)
        embed.add_field(name='Allow Bot Posts', value=str(board.allow_bot_posts))
        embed.add_field(name=f'Channel{"s" if len(board.channels) > 1 else ""}', value='\n'.join(channel_mentions))
        await ctx.send(embed=embed)

    @emoteboard.command(name='add', aliases=['create'])
    @ext.required_claims(Claims.manage_emote_boards)
    @ext.long_help('Add an emote board to the server.')
    @ext.short_help('Add an emote board.')
    @ext.example(['board add :star: starboard #starboard', 'board add :a_custom_emote: myboard #my-board'])
    async def add_board(self,
                        ctx: ext.ClemBotCtx,
                        emote: discord.PartialEmoji,
                        name: str,
                        channel: discord.TextChannel) -> None:
        if board := (await self._get_board(emote, ctx) or await self._get_board(name, ctx)):
            embed = discord.Embed(title='Error', color=Colors.Error)
            embed.description = f'Could not create emote board: {board.emote} **{board.name}** already exists.'
            embed.set_footer(text=str(ctx.author), icon_url=ctx.author.display_avatar.url)
            msg = await ctx.send(embed=embed)
            await self.bot.messenger.publish(Events.on_set_deletable, msg=msg, author=ctx.author, timeout=60)
            return

        pass

    @emoteboard.command(name='remove', aliases=['delete'])
    @ext.required_claims(Claims.manage_emote_boards)
    @ext.long_help('Remove an emote board from the server.')
    @ext.short_help('Remove an emote board.')
    @ext.example(['board remove starboard', 'board remove :star:'])
    async def remove_board(self, ctx: ext.ClemBotCtx, emoteboard: EMOTEBOARD_TYPE) -> None:
        pass

    @emoteboard.command(name='leaderboard', aliases=['top'])
    @ext.long_help('View the leaderboard for all emote boards or for a specific emote board.')
    @ext.short_help('View the leaderboard.')
    @ext.example(['board leaderboard', 'board leaderboard :star:', 'board leaderboard starboard'])
    async def leaderboard(self, ctx: ext.ClemBotCtx, emoteboard: EMOTEBOARD_TYPE | None = None) -> None:
        pass

    @emoteboard.group(name='set')
    @ext.long_help('Edit your emote board.')
    @ext.short_help('Edit specific values of your emote board.')
    @ext.example('help emoteboard set')
    async def set_group(self, ctx: ext.ClemBotCtx) -> None:
        return

    @set_group.command(pass_context=True, name='threshold', aliases=['limit', 'reactions', 'emotes'])
    @ext.required_claims(Claims.manage_emote_boards)
    @ext.long_help('Set the number of reactions a message must get in order for a post to be made.')
    @ext.short_help('Set the reaction threshold for an emote board.')
    @ext.example(['board set reactions starboard 4', 'board set reactions :star: 5'])
    async def set_threshold(self, ctx: ext.ClemBotCtx, emoteboard: EMOTEBOARD_TYPE, threshold: int) -> None:
        pass

    @set_group.command(pass_context=True, name='bots', aliases=['bot', 'allow_bots'])
    @ext.required_claims(Claims.manage_emote_boards)
    @ext.long_help('Sets whether messages authored by bots can be posted to an emote board.')
    @ext.short_help('Set whether bots can post to an emote board.')
    @ext.example(['board set bots starboard false', 'board set bots :star: true'])
    async def set_bots(self, ctx: ext.ClemBotCtx, emoteboard: EMOTEBOARD_TYPE, bots: bool) -> None:
        pass

    @set_group.command(pass_context=True, name='emote', aliases=['emoji'])
    @ext.required_claims(Claims.manage_emote_boards)
    @ext.long_help('Sets the emote that belongs to the given emote board.')
    @ext.short_help('Sets the emote for a board.')
    @ext.example(['board set emote starboard :star:', 'board set emote starboard :a_custom_emote:'])
    async def set_emote(self, ctx: ext.ClemBotCtx, board_name: str, emote: discord.PartialEmoji) -> None:
        pass

    @emoteboard.group(name='channel')
    @ext.long_help('Add or remove a channel for ClemBot to post to for a specific emote board.')
    @ext.short_help('Add or remove a channel from an emote board.')
    @ext.example('help emoteboard channel')
    async def channel_group(self, ctx: ext.ClemBotCtx) -> None:
        return

    @channel_group.command(pass_context=True, name='add')
    @ext.required_claims(Claims.manage_emote_boards)
    @ext.long_help('Add a channel for ClemBot to post messages to for the given emote board.')
    @ext.short_help('Add a channel for an emote board.')
    @ext.example(['board channel add :star: #my-cool-channel', 'board channel add starboard #another-channel'])
    async def channel_add(self, ctx: ext.ClemBotCtx, emoteboard: EMOTEBOARD_TYPE, channel: discord.TextChannel) -> None:
        pass

    @channel_group.command(pass_context=True, name='remove', aliases=['delete'])
    @ext.required_claims(Claims.manage_emote_boards)
    @ext.long_help('Remove a channel from channels ClemBot should post to for the given emote board.')
    @ext.short_help('Remove a channel for an emote board.')
    @ext.example(['board channel remove :star: #my-cool-channel', 'board channel remove starboard #another-channel'])
    async def channel_remove(self,
                             ctx: ext.ClemBotCtx,
                             emoteboard: EMOTEBOARD_TYPE,
                             channel: discord.TextChannel) -> None:
        pass

    async def _get_board(self, eb: EMOTEBOARD_TYPE, ctx: ext.ClemBotCtx, send_error: bool = False) -> EmoteBoard | None:
        """
        Gets the emote board with the following name or emote that belongs to the guild.
        Checks against both the emote board name and emote for consistency.
        Returns None if a board with the given name or emote does not exist in the guild.
        """
        if not ctx.guild:
            return None

        value = (eb if isinstance(eb, str) else str(eb)).casefold()
        for board in await self.bot.emote_board_route.get_emote_boards(ctx.guild):
            if board.name.casefold() == value or board.emote.casefold() == value:
                return board

        if not send_error:
            return None

        await self._error_embed(ctx, f'An emote board with the given {"emote" if self._is_emoji(eb) else "name"} '
                                     f'{eb if self._is_emoji(eb) else f"`{eb}`"} could not be found.')
        return None

    async def _error_embed(self, ctx: ext.ClemBotCtx, description: str) -> None:
        embed = discord.Embed(title='Error', color=Colors.Error)
        embed.description = description
        embed.set_footer(text=str(ctx.author), icon_url=ctx.author.display_avatar.url)
        message = await ctx.send(embed=embed)
        await self.bot.messenger.publish(Events.on_set_deletable, msg=message, author=ctx.author, timeout=60)

    def _is_emoji(self, s: EMOTEBOARD_TYPE) -> bool:
        return isinstance(s, discord.PartialEmoji) or emoji.is_emoji(s)

    def _chunked_boards(self, boards: list[EmoteBoard], n: int, ctx: ext.ClemBotCtx, title: str) -> list[discord.Embed]:
        """Chunks the given boards into a markdown-ed list of n-sized items (row * col)"""
        pages = []
        for chunk in chunk_sequence(boards, n):
            embed = discord.Embed(color=Colors.ClemsonOrange, title=title)
            embed.description = f'Here are the emote boards for **{ctx.guild.name}**.'
            for board in chunk:
                embed.add_field(name=board.name, value=board.emote)
            pages.append(embed)

        return pages


async def setup(bot: ClemBot) -> None:
    await bot.add_cog(EmoteBoardCog(bot))
