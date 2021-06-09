import logging
import typing as t

import discord
import discord.ext.commands as commands

import bot.bot_secrets as bot_secrets
import bot.extensions as ext
from bot.consts import Claims, Colors

log = logging.getLogger(__name__)


class CustomPrefixCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @ext.group(case_insensitive=True, invoke_without_command=True, aliases=['prefixs'])
    @ext.long_help(
        'Lists the current prefix or configures the command prefix that the bot will respond too'
    )
    @ext.short_help('Configure a custom command prefix')
    @ext.example(('prefix', 'prefix ?', 'prefix >>'))
    async def prefix(self, ctx, *, prefix: t.Optional[str] = None):
        # get_prefix returns two mentions as the first possible prefixes in the tuple,
        # those are global so we dont care about them
        prefixes = (await self.bot.get_prefix(ctx.message))[2:]

        if not prefix:
            embed = discord.Embed(title='Current Active Prefixes',
                                  description=f'```{", ".join(prefixes)}```',
                                  color=Colors.ClemsonOrange)

            return await ctx.send(embed=embed)

        if prefix in await self.bot.get_prefix(ctx.message):
            embed = discord.Embed(title='Error', color=Colors.Error)
            embed.add_field(name='Invalid prefix', value=f'"{prefix}" is already the prefix for this guild')
            await ctx.send(embed=embed)
            return

        if '`' in prefix:
            embed = discord.Embed(title='Error', color=Colors.Error)
            embed.add_field(name='Invalid prefix', value='Prefix can not contain " ` "')
            await ctx.send(embed=embed)
            return

        await self.bot.custom_prefix_route.set_custom_prefix(ctx.guild.id, prefix)

        embed = discord.Embed(color=Colors.ClemsonOrange)
        embed.add_field(name='Prefix changed   :white_check_mark:', value=f'New Prefix: ```{prefix}```')
        await ctx.send(embed=embed)

    @prefix.command(pass_context=True, aliases=['revert'])
    @ext.required_claims(Claims.custom_prefix_set)
    @ext.long_help(
        'resets the bot prefix to the default'
    )
    @ext.short_help('resets a custom prefix')
    @ext.example('prefix set')
    async def reset(self, ctx):
        default_prefix = bot_secrets.secrets.bot_prefix

        if default_prefix in await self.bot.get_prefix(ctx.message):
            embed = discord.Embed(title='Error', color=Colors.Error)
            embed.add_field(name='Invalid prefix', value=f'"{default_prefix}" Prefix is already the default')
            await ctx.send(embed=embed)
            return

        await self.bot.custom_prefix_route.set_custom_prefix(ctx.guild.id, default_prefix)

        embed = discord.Embed(color=Colors.ClemsonOrange)
        embed.add_field(
            name='Prefix reset   :white_check_mark:',
            value=f'New Prefix: ```{default_prefix}```')

        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(CustomPrefixCog(bot))
