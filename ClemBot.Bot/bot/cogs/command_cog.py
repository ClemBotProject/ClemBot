# type: ignore
import typing as t

import discord
import discord.ext.commands as commands
from discord import TextChannel
from discord.ext.commands import Context

import bot.extensions as ext
from bot.clem_bot import BotT, ClemBot
from bot.consts import Claims, Colors
from bot.messaging.events import Events
from bot.models.command_models import CommandModel


class CommandConverter(commands.Converter[ext.ClemBotCommand | None]):
    async def convert(self, ctx: Context[BotT], argument: str) -> ext.ClemBotCommand | None:
        return ctx.bot.get_command(argument)


class CommandCog(commands.Cog):
    def __init__(self, bot: ClemBot) -> None:
        self.bot = bot

    @ext.group(aliases=["cmd"], case_insensitive=True, invoke_without_command=True)
    @ext.allow_disable(False)
    @ext.long_help("Check if a command is enabled or disabled.")
    @ext.short_help("Check if a command is enabled.")
    @ext.example(["command slots", "command help"])
    async def command(self, ctx: ext.ClemBotCtx, cmd: CommandConverter) -> None:
        if not cmd:
            await self._error_embed(ctx, f"Command not found.")
            return
        model = await self.bot.commands_route.get_details(ctx.guild.id, ctx.channel.id, cmd.name)
        assert model is not None
        (name, value) = self._disabled_in_field(model)
        embed = discord.Embed(title="⚙️ Command Details", color=Colors.ClemsonOrange)
        embed.add_field(name="Name", value=f"`{cmd.name}`")
        embed.add_field(name="Allows Disabling", value=cmd.allow_disable, inline=False)
        embed.add_field(name=name, value=value)
        if cmd.allow_disable:
            opp_mode = "enable" if model.disabled else "disable"
            embed.set_footer(
                text=f"You can {opp_mode} this command by typing "
                f'"{ctx.prefix}cmd {opp_mode} {cmd.name}"'
            )
        await ctx.send(embed=embed)

    @command.command(aliases=["on"])
    @ext.required_claims(Claims.manage_commands)
    @ext.long_help("Enable a command server-wide or in a specific channel.")
    @ext.short_help("Enable a command.")
    @ext.example(["command enable search", "command enable slots #my-channel"])
    async def enable(
        self, ctx: ext.ClemBotCtx, cmd: CommandConverter, channel: t.Optional[TextChannel]
    ) -> None:
        if not cmd:
            await self._error_embed(ctx, f"Command not found.")
            return
        # not going to check if the command allows disabling in the off-chance it's been changed from
        # allowing disabling (and was disabled) to then disallowing disabling. this would soft-lock the cmd.
        model = await self.bot.commands_route.get_details(ctx.guild.id, ctx.channel.id, cmd.name)
        assert model is not None
        if not model.disabled:
            await self._error_embed(ctx, f"The command `{cmd.name}` is not disabled.")
            return
        if channel is not None and channel.id not in model.channel_ids:
            await self._error_embed(
                ctx, f"The command `{cmd.name}` is not disabled in {channel.mention}."
            )
            return
        await self.bot.commands_route.enable_command(
            cmd.name, ctx.guild.id, channel.id if channel is not None else None
        )
        embed = discord.Embed(title="⚙️ Command Enabled", color=Colors.ClemsonOrange)
        embed.add_field(name="Command Name", value=f"`{cmd.name}`")
        embed.add_field(
            name="Enabled" if channel is None else "Enabled In",
            value="Server-wide" if channel is None else channel.mention,
            inline=False,
        )
        await ctx.send(embed=embed)

    @command.command(aliases=["off"])
    @ext.required_claims(Claims.manage_commands)
    @ext.long_help(
        "Disable a command server-wide or in a specific channel with the option to fail silently."
    )
    @ext.short_help("Disable a command.")
    @ext.example(
        [
            "command disable slots",
            "command disable eval #my-channel",
            "command disable info #my-channel true",
        ]
    )
    async def disable(
        self,
        ctx: ext.ClemBotCtx,
        cmd: CommandConverter,
        channel: t.Optional[TextChannel],
        silent: bool = False,
    ) -> None:
        if not cmd:
            await self._error_embed(ctx, f"Command not found.")
            return
        if not cmd.allow_disable:
            await self._error_embed(ctx, f"Command `{cmd.name}` cannot be disabled.")
            return
        model = await self.bot.commands_route.get_details(ctx.guild.id, ctx.channel.id, cmd.name)
        assert model is not None
        if len(model.channel_ids) == 0 and model.disabled:
            await self._error_embed(
                ctx, f"The command `{cmd.name}` is already disabled server-wide."
            )
            return
        if channel is not None and channel.id in model.channel_ids:
            await self._error_embed(
                ctx, f"The command `{cmd.name}` is already disabled in {channel.mention}."
            )
            return
        await self.bot.commands_route.disable_command(
            cmd.name, ctx.guild.id, channel.id if channel is not None else None, silent
        )
        embed = discord.Embed(title="⚙️ Command Disabled", color=Colors.ClemsonOrange)
        embed.add_field(name="Command Name", value=f"`{cmd.name}`")
        embed.add_field(
            name="Disabled" if channel is None else "Disabled In",
            value="Server-wide" if channel is None else channel.mention,
            inline=False,
        )
        embed.add_field(name="Silently Fail", value=silent)
        await ctx.send(embed=embed)

    def _disabled_in_field(self, model: CommandModel) -> tuple[str, str]:
        if not model.disabled:
            return "Disabled", "False"
        if len(model.channel_ids) == 0:
            return "Disabled", "Server-wide"
        list_of_channels = []
        for channel_id in model.channel_ids:
            channel = self.bot.get_channel(channel_id)
            if channel is None or isinstance(channel, discord.abc.PrivateChannel):
                continue
            list_of_channels.append(channel.mention)
        return "Disabled In", "\n".join(list_of_channels)

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
