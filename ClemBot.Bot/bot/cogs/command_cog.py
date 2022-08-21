import typing as t

import discord
import discord.ext.commands as commands
from discord import TextChannel

import bot.extensions as ext
from bot.clem_bot import ClemBot
from bot.consts import Claims, Colors
from bot.messaging.events import Events
from bot.models.command_models import CommandModel


class CommandCog(commands.Cog):

    def __init__(self, bot: ClemBot) -> None:
        self.bot = bot

    @ext.group(aliases=['cmd'], case_insensitive=True, invoke_without_command=True)
    @ext.allow_disable(False)
    @ext.long_help('Check if a command is enabled or disabled.')
    @ext.short_help('Check if a command is enabled.')
    async def command(self, ctx: ext.ClemBotCtx, cmd: str) -> None:
        command = self.bot.get_command(cmd)
        if not command:
            await self._error_embed(ctx, f'Command `{cmd}` not found.')
            return
        command = t.cast(ext.ClemBotCommand, command)
        model = await self.bot.commands_route.get_details(ctx.guild.id, ctx.channel.id, command.name)
        assert model is not None
        (name, value, inline) = self._disabled_in_field(model)
        embed = discord.Embed(title='⚙️ Command Details', color=Colors.ClemsonOrange)
        embed.add_field(name='Name', value=command.name)
        embed.add_field(name='Can Be Disabled', value=str(command.allow_disable))
        embed.add_field(name=name, value=value, inline=inline)
        opp_mode = 'enable' if model.disabled else 'disable'
        embed.set_footer(text=f"You can {opp_mode} this command by typing "
                              f"\"{ctx.prefix}cmd {opp_mode} {command.name}\"")
        pass

    @command.command(aliases=['on'])
    @ext.required_claims(Claims.manage_commands)
    @ext.long_help('Enable a command server-wide or in a specific channel.')
    @ext.short_help('Enable a command.')
    async def enable(self, ctx: ext.ClemBotCtx, cmd: str, channel: t.Optional[TextChannel]) -> None:
        pass

    @command.command(aliases=['off'])
    @ext.required_claims(Claims.manage_commands)
    @ext.long_help('Disable a command server-wide.')
    @ext.short_help('Disable a command.')
    async def disable(self, ctx: ext.ClemBotCtx, cmd: str, channel: t.Optional[TextChannel], silent: bool = False) -> None:
        command = self.bot.get_command(cmd)
        if not command:
            await self._error_embed(ctx, f'Command `{cmd}` not found.')
            return
        command = t.cast(ext.ClemBotCommand, command)
        if not command.allow_disable:
            await self._error_embed(ctx, f'Command `{cmd}` cannot be disabled.')
            return
        # todo
        pass

    def _disabled_in_field(self, model: CommandModel) -> tuple[str, str, bool]:
        if not model.disabled:
            return 'Disabled', 'False', True
        if len(model.channel_ids) == 0:
            return 'Disabled', 'Server-wide', True
        list_of_channels = []
        for channel_id in model.channel_ids:
            channel = self.bot.get_channel(channel_id)
            if channel is None or isinstance(channel, discord.abc.PrivateChannel):
                continue
            list_of_channels.append(channel.mention)
        return 'Disabled In', '\n'.join(list_of_channels), False

    async def _error_embed(self, ctx: ext.ClemBotCtx, desc: str) -> None:
        """Shorthand for sending an error message w/ consistent formatting."""
        embed = discord.Embed(title="Error", color=Colors.Error, description=desc)
        embed.set_footer(text=str(ctx.author), icon_url=ctx.author.display_avatar.url)
        msg = await ctx.send(embed=embed)
        await self.bot.messenger.publish(
            Events.on_set_deletable, msg=msg, author=ctx.author, timeout=60
        )


async def setup(bot: ClemBot) -> None:
    await bot.add_cog(CommandCog(bot))
