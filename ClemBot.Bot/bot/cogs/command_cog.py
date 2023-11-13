import typing as t

import discord
import discord.ext.commands as commands
from discord import TextChannel

import bot.extensions as ext
from bot.clem_bot import ClemBot
from bot.consts import Claims, Colors
from bot.messaging.events import Events
from bot.models.command_models import CommandModel
from bot.utils.converters import CommandConverter


class CommandCog(commands.Cog):
    def __init__(self, bot: ClemBot) -> None:
        self.bot = bot

    @ext.group(aliases=["cmd"], case_insensitive=True, invoke_without_command=True)
    @ext.ban_disabling()
    @ext.long_help("Check if a command is enabled or disabled.")
    @ext.short_help("Check if a command is enabled.")
    @ext.example(["command slots", "command help"])
    @ext.docs("CommandRestrictions", "command")
    async def command(
        self,
        ctx: ext.ClemBotCtx,
        command: t.Annotated[list[ext.ClemBotCommand], commands.Greedy[CommandConverter]],
    ) -> None:
        if not command:
            await self._error_embed(ctx, "Command not found.")
            return

        cmd = command[-1]

        model = await self.bot.commands_route.get_details(ctx.guild.id, cmd.qualified_name)
        assert model is not None

        (name, value) = self._disabled_in_field(model)
        embed = discord.Embed(title="⚙️ Command Details", color=Colors.ClemsonOrange)
        embed.add_field(name="Name", value=f"`{cmd.qualified_name}`")
        embed.add_field(name="Allows Disabling", value=cmd.allow_disable, inline=False)
        embed.add_field(name=name, value=value)

        if model.white_listed_channel_ids:
            whitelisted_channels = []
            for channel_id in model.white_listed_channel_ids:
                channel = self.bot.get_channel(channel_id)

                if channel is None or isinstance(channel, discord.abc.PrivateChannel):
                    whitelisted_channels.append(str(channel_id))
                else:
                    whitelisted_channels.append(channel.mention)
            embed.add_field(name="Enabled in", value="\n".join(whitelisted_channels))

        if cmd.allow_disable:
            opp_mode = "enable" if model.guild_disabled else "disable"
            embed.set_footer(
                text=f"You can {opp_mode} this command globally by typing "
                f'"{await self.bot.current_prefix(ctx)}cmd {opp_mode} {cmd.qualified_name}"'
            )
        await ctx.send(embed=embed)

    @command.command(aliases=["on"])
    @ext.ban_disabling()
    @ext.required_claims(Claims.command_restrictions_edit)
    @ext.long_help("Enable a command server-wide or in a specific channel.")
    @ext.short_help("Enable a command.")
    @ext.example(["command enable search", "command enable slots #my-channel"])
    @ext.docs("CommandRestrictions", "enable")
    async def enable(
        self,
        ctx: ext.ClemBotCtx,
        command: t.Annotated[list[ext.ClemBotCommand], commands.Greedy[CommandConverter]],
        channel: t.Optional[TextChannel],
    ) -> None:
        if not command:
            await self._error_embed(ctx, "Command not found.")
            return

        cmd = command[-1]

        # not going to check if the command allows disabling in the off-chance it's been changed from
        # allowing disabling (and was disabled) to then disallowing disabling. this would soft-lock the cmd.
        model = await self.bot.commands_route.get_details(ctx.guild.id, cmd.qualified_name)
        assert model is not None

        # Check if the channel is already enabled globally
        if not model.guild_disabled and not channel:
            await self._error_embed(ctx, f"The command `{cmd.qualified_name}` is already enabled.")
            return

        # Check if the channel is disabled guild wide or has a channel restriction
        if model.guild_disabled and (channel and channel.id in model.white_listed_channel_ids):
            await self._error_embed(
                ctx, f"The command `{cmd.qualified_name}` is already enabled in {channel.mention}."
            )
            return

        await self.bot.commands_route.enable_command(
            cmd.qualified_name, ctx.guild.id, channel.id if channel is not None else None
        )
        embed = discord.Embed(title="⚙️ Command Enabled", color=Colors.ClemsonOrange)
        embed.add_field(name="Command Name", value=f"`{cmd.qualified_name}`")
        embed.add_field(
            name="Enabled" if channel is None else "Enabled In",
            value="Server-wide" if channel is None else channel.mention,
            inline=False,
        )
        await ctx.send(embed=embed)

    @command.command(aliases=["off"])
    @ext.required_claims(Claims.command_restrictions_edit)
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
    @ext.docs("CommandRestrictions", "disable")
    async def disable(
        self,
        ctx: ext.ClemBotCtx,
        command: t.Annotated[list[ext.ClemBotCommand], commands.Greedy[CommandConverter]],
        channel: t.Optional[TextChannel],
        silent: t.Annotated[bool, t.Optional[bool]] = False,
    ) -> None:

        if not command:
            await self._error_embed(ctx, "Command not found.")
            return

        # If the parse view did not make it to the end of the argument list then we
        # know that we failed to parse at least one of the inputted values
        # EX: !command disable tag invalidcommand #some-channel true
        # invalidcommand will fail to parse because it doesn't exist
        if not ctx.view.eof:
            await self._error_embed(
                ctx, f"Argument parsing failed on input value `{ctx.current_argument}`"
            )
            return

        # The greedy converter returns a list of all the valid commands, grab the last one as that is the full commmand inputted
        cmd = command[-1]

        if not cmd.allow_disable:
            await self._error_embed(ctx, f"Command `{cmd.qualified_name}` cannot be disabled.")
            return

        model = await self.bot.commands_route.get_details(ctx.guild.id, cmd.qualified_name)

        if not model:
            await self._error_embed(ctx, "Retrieving Command restriction details failed")
            return

        # Check if the channel is disabled guild wide or has a channel restriction
        if model.guild_disabled and (channel and channel.id not in model.white_listed_channel_ids):
            if not channel:
                await self._error_embed(
                    ctx, f"The command `{cmd.qualified_name}` is already disabled."
                )
            else:
                await self._error_embed(
                    ctx,
                    f"The command `{cmd.qualified_name}` is already disabled in {channel.mention}.",
                )
            return

        await self.bot.commands_route.disable_command(
            cmd.qualified_name, ctx.guild.id, channel.id if channel is not None else None, silent
        )
        embed = discord.Embed(title="⚙️ Command Disabled", color=Colors.ClemsonOrange)
        embed.add_field(name="Command Name", value=f"`{cmd.qualified_name}`")
        embed.add_field(
            name="Disabled" if channel is None else "Disabled In",
            value="Server-wide" if channel is None else channel.mention,
            inline=False,
        )
        embed.add_field(name="Silently Fail", value=silent)
        await ctx.send(embed=embed)

    def _disabled_in_field(self, model: CommandModel) -> tuple[str, str]:
        if not model.guild_disabled and len(model.black_listed_channel_ids) == 0:
            return "Disabled", "False"

        if not model.black_listed_channel_ids:
            return "Disabled", "Server-wide"

        blacklisted_channels = []
        for blacklist in model.black_listed_channel_ids:

            channel = self.bot.get_channel(blacklist.channel_id)

            if channel is None or isinstance(channel, discord.abc.PrivateChannel):
                blacklisted_channels.append(str(blacklist.channel_id))
            else:
                s = f"{channel.mention} Silently Fail: `{blacklist.silently_fail}`"
                blacklisted_channels.append(s)

        return "Disabled In", "\n".join(blacklisted_channels)

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
