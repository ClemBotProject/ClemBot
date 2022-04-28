import logging
import typing as t

import discord
import discord.ext.commands as commands

import bot.extensions as ext
from bot.consts import Claims, Colors

log = logging.getLogger(__name__)

DEFAULT_TAG_PREFIX = '$'

class CustomTagPrefixCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @ext.group(case_insensitive=True, invoke_without_command=True, aliases=['tagprefixs'])
    @ext.long_help(
        'Lists the current tag prefix or configures the command prefix that the bot will respond too'
    )
    @ext.short_help('Configure a custom command tag prefix')
    @ext.example(('tagprefix', 'tagprefix ?', 'tagprefix >>'))
    async def tagprefix(self, ctx, *, tagprefix: t.Optional[str] = None):
        # get_prefix returns two mentions as the first possible prefixes in the tuple,
        # those are global so we dont care about them
        tag_prefixes = (await self.bot.get_tag_prefix(ctx.message))

        if not tagprefix:
            embed = discord.Embed(title='Current Active Tag Prefixes',
                                  description=f'```{", ".join(tag_prefixes)}```',
                                  color=Colors.ClemsonOrange)

            return await ctx.send(embed=embed)

        if tagprefix in await self.bot.get_tag_prefix(ctx.message):
            embed = discord.Embed(title='Error', color=Colors.Error)
            embed.add_field(name='Invalid tag prefix', value=f'"{tagprefix}" is already the tag prefix for this guild')
            await ctx.send(embed=embed)
            return

        if '`' in tagprefix:
            embed = discord.Embed(title='Error', color=Colors.Error)
            embed.add_field(name='Invalid tag prefix', value='Tag Prefix can not contain " ` "')
            await ctx.send(embed=embed)
            return

        await self.bot.custom_tag_prefix_route.set_custom_tag_prefix(ctx.guild.id, tagprefix)

        embed = discord.Embed(color=Colors.ClemsonOrange)
        embed.add_field(name='Tag Prefix changed   :white_check_mark:', value=f'New Prefix: ```{tagprefix}```')
        await ctx.send(embed=embed)

    @tagprefix.command(pass_context=True, aliases=['revert'])
    @ext.required_claims(Claims.custom_tag_prefix_set)
    @ext.long_help(
        'resets the bot tag prefix to the default'
    )
    @ext.short_help('resets a custom tag prefix')
    @ext.example('tag prefix set')
    async def reset(self, ctx):
        default_tag_prefix = DEFAULT_TAG_PREFIX

        if default_tag_prefix in await self.bot.get_tag_prefix(ctx.message):
            embed = discord.Embed(title='Error', color=Colors.Error)
            embed.add_field(name='Invalid tag prefix', value=f'"{default_tag_prefix}" Tag Prefix is already the default')
            await ctx.send(embed=embed)
            return

        await self.bot.custom_tag_prefix_route.set_custom_tag_prefix(ctx.guild.id, default_tag_prefix)

        embed = discord.Embed(color=Colors.ClemsonOrange)
        embed.add_field(
            name='Tag Prefix reset   :white_check_mark:',
            value=f'New Tag Prefix: ```{default_tag_prefix}```')

        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(CustomTagPrefixCog(bot))
