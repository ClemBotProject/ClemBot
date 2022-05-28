import logging
from collections.abc import Iterable

import discord
import discord.ext.commands as commands

import bot.extensions as ext
from bot.consts import Colors
from bot.messaging.events import Events
import bot.bot_secrets as bot_secrets

log = logging.getLogger(__name__)
HELP_EMBED_SIZE = 15


class HelpCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.commands = []

    @ext.command()
    async def help(self, ctx, *, command_name=None):
        if command_name:
            command = self.find_command(self.bot, command_name.lower())
            if isinstance(command, ext.ClemBotCommand):
                await self.send_command_help(ctx, command)
            elif isinstance(command, ext.ClemBotGroup):
                await self.send_group_help(ctx, command)
            else:
                await self.send_default_help(ctx, f'Command: {command_name} not found, here is a list of all my commands')
        else:
            await self.send_default_help(ctx)

    async def send_group_help(self, ctx, command: ext.ClemBotGroup):
        if command.hidden and not await self.bot.is_owner(ctx.author):
            return await self.send_default_help(ctx, f'Command: {command.name} not found.')

        prefix = await self.bot.current_prefix(ctx)

        embed = discord.Embed(title=f'```{prefix}{command.qualified_name}```',
                              description=f'for more info on a subcommand run `{prefix}help <SubCommandName>`',
                              color=Colors.ClemsonOrange)
        embed.add_field(name='Description', value=command.long_help or 'No description provided', inline=False)

        embed.add_field(
            name='Usage Example',
            value=self.get_example(command.example, prefix) or 'No example provided',
        )

        if command.signature:
            embed.add_field(name='Signature', value=command.signature)

        if len(command.aliases) > 0:
            embed.add_field(name='Aliases', value=', '.join(command.aliases))

        com_repr = '\n'.join(self.get_commands_repr(
            command.commands,
            f'{prefix}{command.qualified_name} ',
            await self.bot.is_owner(ctx.author)
        ))
        embed.add_field(name='Subcommands', value=com_repr or 'No example provided', inline=False)

        embed.set_author(name=f'{self.bot.user.name} - Help', url=bot_secrets.secrets.site_url, icon_url=self.bot.user.display_avatar.url)
        embed.add_field(name='Website', value=f'For more information on my commands please visit my website [clembot.io]({bot_secrets.secrets.site_url})',
                        inline=False)

        await ctx.send(embed=embed)

    async def send_command_help(self, ctx, command: ext.ClemBotCommand):
        if command.hidden and not await self.bot.is_owner(ctx.author):
            return await self.send_default_help(ctx, f'Command {command.name} not found.')

        prefix = await self.bot.current_prefix(ctx)

        embed = discord.Embed(title=f'```{prefix}{command.qualified_name}```', color=Colors.ClemsonOrange)
        embed.add_field(name='Description', value=command.long_help or 'No description provided', inline=False)

        if command.signature:
            embed.add_field(name='Signature', value=command.signature)
        if len(command.aliases) > 0:
            embed.add_field(name='Aliases', value=', '.join(command.aliases))

        embed.add_field(
            name='Usage Example',
            value=self.get_example(command.example, prefix) or 'No example provided',
            inline=False)
        embed.add_field(name='Website', value=f'For more information on my commands please visit my website [clembot.io]({bot_secrets.secrets.site_url})',
                        inline=False)
        embed.set_author(name=f'{self.bot.user.name} - Help', url=bot_secrets.secrets.site_url, icon_url=self.bot.user.display_avatar.url)

        await ctx.send(embed=embed)

    def find_command(self, parent: commands.Command, command_name: str):
        """
        Recursively searches the command tree to find a given command, if none found then returns None
        """
        if isinstance(parent, commands.Bot):
            found = None
            for c in parent.commands:
                if result := self.find_command(c, command_name):
                    found = result
            return found

        if command_name in (parent.qualified_name, *parent.aliases):
            return parent

        if isinstance(parent, ext.ClemBotGroup):
            for c in parent.commands:
                if result := self.find_command(c, command_name):
                    return result
        return None

    async def send_default_help(self, ctx, title=None):

        prefix = await self.bot.current_prefix(ctx)

        cog_embeds = []
        commands_str = self.get_commands_repr(self.bot.commands, prefix, await self.bot.is_owner(ctx.author))

        for command in self.chunk_list(commands_str, HELP_EMBED_SIZE):
            embed = discord.Embed(
                title=title,
                description=f'for more info on a command run `{prefix}help <CommandName>`',
                color=Colors.ClemsonOrange)

            embed.set_author(name=f'{self.bot.user.name} - Help', url=bot_secrets.secrets.site_url, icon_url=self.bot.user.display_avatar.url)
            embed.add_field(name='Commands', value='\n'.join(command))
            embed.add_field(name='Website', value=f'For more information on my commands please visit my website [clembot.io]({bot_secrets.secrets.site_url})',
                            inline=False)

            cog_embeds.append(embed)

        await self.bot.messenger.publish(Events.on_set_pageable_embed,
                                         pages=cog_embeds,
                                         author=ctx.author,
                                         channel=ctx.channel,
                                         timeout=360
                                         )

    def get_commands_repr(self, commands, prefix, is_owner: bool = False):
        commands_repr = []
        for command in commands:
            # check to see if a command has been hidden from the public help command
            if command.hidden and not is_owner:
                continue
            if not isinstance(command, ext.ExtBase):
                log.warning(f'Help command invoked but none Clembot ext command found name: {command.name}, skipping command help')
                continue

            command_help = command.short_help or 'None'
            commands_repr.append(f'`{prefix}{command.name}`: {command_help}')

        commands_repr.sort()
        return commands_repr

    def get_example(self, ex, prefix, qualified_name: str = None):
        if isinstance(ex, str):
            return f'`{prefix}{ex}`'
        elif isinstance(ex, Iterable):
            return '\n'.join(f'`{prefix}{i}`' for i in ex)
        elif not ex:
            return None
        raise TypeError('Help example must be of type iterable or str')

    def chunk_list(self, lst, n):
        """Yield successive n-sized chunks from lst."""
        for i in range(0, len(lst), n):
            yield lst[i:i + n]


def setup(bot):
    bot.add_cog(HelpCog(bot))
