import typing as t

import discord
import discord.ext.commands as commands

import bot.extensions as ext
from bot.clem_bot import ClemBot
from bot.consts import Claims, Colors, DesignatedChannels, Moderation
from bot.messaging.events import Events
from bot.utils.converters import FutureDuration
from bot.utils.logging_utils import get_logger
from bot.utils.user_choice import UserChoice
from bot.utils.helpers import format_duration

log = get_logger(__name__)


class MuteCog(commands.Cog):
    def __init__(self, bot: ClemBot):
        self.bot = bot

    @ext.command()
    @ext.long_help("Mutes a user for a given amount of time with an optional reason")
    @ext.short_help("Mutes a user")
    @ext.example(("mute @SomeUser 1d Timeout", "mute @SomUser 2d1h5m A much longer timeout"))
    @ext.required_claims(Claims.moderation_mute)
    async def mute(
        self,
        ctx: ext.ClemBotCtx,
        subject: discord.Member,
        duration: FutureDuration,
        *,
        reason: str | None,
    ) -> None:
        if reason and len(reason) > Moderation.max_reason_length:
            embed = discord.Embed(title="Error", color=Colors.Error)
            embed.add_field(
                name="Reason",
                value=f"Reason length is greater than max {Moderation.max_reason_length} characters.",
            )
            embed.set_author(name=str(ctx.author), icon_url=ctx.author.display_avatar.url)
            await ctx.send(embed=embed)
            return

        if ctx.author.top_role.position <= subject.top_role.position:
            embed = discord.Embed(color=Colors.Error)
            embed.title = "Error: Invalid Permissions"
            embed.add_field(
                name="Reason", value="Cannot moderate someone with the same rank or higher"
            )
            embed.set_author(name=str(ctx.author), icon_url=ctx.author.display_avatar.url)
            await ctx.send(embed=embed)
            return

        mute_role = discord.utils.get(ctx.guild.roles, name=Moderation.mute_role_name)
        if not mute_role:
            if not await self._create_mute_role(ctx):
                return

        mutes = await self.bot.moderation_route.get_guild_mutes_user(ctx.guild.id, subject.id)
        if any(i.active for i in mutes):
            embed = discord.Embed(color=Colors.Error)
            embed.title = "Error: Current Active Mute"
            embed.add_field(name="Reason", value="Cannot mute someone who is already muted")
            embed.set_author(name=str(ctx.author), icon_url=ctx.author.display_avatar.url)
            await ctx.send(embed=embed)
            return

        # Publish that a mute happened
        await self.bot.messenger.publish(
            Events.on_bot_mute,
            guild=ctx.guild,
            author=ctx.author,
            subject=subject,
            duration=duration,
            reason=reason,
        )

        embed = discord.Embed(color=Colors.ClemsonOrange)
        embed.title = f"{subject} Muted :mute:"
        embed.set_author(name=str(ctx.author), icon_url=ctx.author.display_avatar.url)
        embed.set_thumbnail(url=subject.display_avatar.url)
        embed.description = f"**{format_duration(duration)}** \n{reason}"

        await ctx.send(embed=embed)

        # Send the mute in the mod channels
        embed = discord.Embed(color=Colors.ClemsonOrange)
        embed.title = "Guild Member Muted :mute:"
        embed.set_author(
            name=f"{ctx.author}\nId: {ctx.author.id}", icon_url=ctx.author.display_avatar.url
        )
        embed.add_field(name=str(subject), value=f"Id: {subject.id}")
        embed.add_field(name="Duration :timer:", value=format_duration(duration))
        embed.add_field(name="Reason :page_facing_up:", value=f"```{reason}```", inline=False)
        embed.add_field(name="Message Link  :rocket:", value=f"[Link]({ctx.message.jump_url})")
        embed.set_thumbnail(url=subject.display_avatar.url)

        await self.bot.messenger.publish(
            Events.on_send_in_designated_channel,
            DesignatedChannels.moderation_log,
            ctx.guild.id,
            embed,
        )

        # Dm the user who was muted
        embed = discord.Embed(color=Colors.ClemsonOrange)
        embed.title = "You have been muted  :mute:"
        embed.set_author(name=str(ctx.author), icon_url=ctx.author.display_avatar.url)

        if ctx.guild.icon:
            embed.set_thumbnail(url=str(ctx.guild.icon.url))

        embed.add_field(name="Duration :timer:", value=format_duration(duration))
        embed.add_field(name="Reason :page_facing_up:", value=f"```{reason}```", inline=False)
        embed.description = f"**Guild:** {ctx.guild.name}"

        try:
            await subject.send(embed=embed)
        except (discord.Forbidden, discord.HTTPException):
            embed = discord.Embed(color=Colors.ClemsonOrange)
            embed.title = f"Dm Mute to {subject} forbidden"
            await self.bot.messenger.publish(
                Events.on_send_in_designated_channel,
                DesignatedChannels.moderation_log,
                ctx.guild.id,
                embed,
            )

    @ext.command()
    @ext.long_help("Unmutes a user for a with an optional reason")
    @ext.short_help("Unmutes a user")
    @ext.example("Unmute @SomeUser Timeout")
    @ext.required_claims(Claims.moderation_mute)
    async def unmute(
        self, ctx: ext.ClemBotCtx, subject: discord.Member, *, reason: str | None
    ) -> None:
        mute_role = discord.utils.get(subject.guild.roles, name=Moderation.mute_role_name)

        if not mute_role:
            embed = discord.Embed(color=Colors.Error)
            embed.title = "Error: Mute role not found"
            embed.add_field(
                name="Reason", value="Run the mute command to initiate mute role activation"
            )
            embed.set_author(name=str(ctx.author), icon_url=ctx.author.display_avatar.url)
            await ctx.send(embed=embed)
            return

        mutes = await self.bot.moderation_route.get_guild_mutes_user(subject.guild.id, subject.id)
        mutes = [mute for mute in mutes if mute.active]

        if not mutes:
            embed = discord.Embed(color=Colors.Error)
            embed.title = "Error: This user has no active mutes"
            embed.set_author(name=str(ctx.author), icon_url=ctx.author.display_avatar.url)
            await ctx.send(embed=embed)
            return

        if reason and len(reason) > Moderation.max_reason_length:
            embed = discord.Embed(title="Error", color=Colors.Error)
            embed.add_field(
                name="Reason",
                value=f"Reason length is greater than max {Moderation.max_reason_length} characters.",
            )
            embed.set_author(name=str(ctx.author), icon_url=ctx.author.display_avatar.url)
            await ctx.send(embed=embed)
            return

        for mute in mutes:
            await self.bot.messenger.publish(
                Events.on_bot_unmute, subject.guild.id, subject.id, mute.id, reason, ctx.author
            )

        embed = discord.Embed(color=Colors.ClemsonOrange)
        embed.title = f"{subject} Unmuted  :speaker:"
        embed.set_author(name=str(ctx.author), icon_url=ctx.author.display_avatar.url)
        embed.add_field(name="Reason :page_facing_up:", value=f"```{reason}```", inline=False)
        embed.set_thumbnail(url=subject.display_avatar.url)

        await ctx.send(embed=embed)

    async def _create_mute_role(self, ctx: ext.ClemBotCtx) -> bool:
        get_input = UserChoice(ctx=ctx, timeout=30)
        choice = await get_input.send_confirmation(
            content="Error: ClemBots Mute role not found. Would you like me to create it?",
            is_error=True,
        )
        if not choice:
            embed = discord.Embed(color=Colors.Error)
            embed.title = "Error: Mute Role not found, Cancelling operation"
            embed.set_author(name=str(ctx.author), icon_url=ctx.author.display_avatar.url)
            return False

        mute_role = await ctx.guild.create_role(name=Moderation.mute_role_name)
        await mute_role.edit(position=ctx.guild.me.top_role.position - 1)
        msg = await ctx.send("Configuring ClemBot Mute role (This might take a minute)")
        for channel in ctx.guild.channels:
            try:
                await channel.set_permissions(
                    mute_role,
                    speak=False,
                    connect=False,
                    stream=False,
                    send_messages=False,
                    send_messages_in_threads=False,
                    create_public_threads=False,
                    create_private_threads=False,
                    send_tts_messages=False,
                    add_reactions=False,
                )
            except:
                pass

        await msg.delete()
        embed = discord.Embed(color=Colors.ClemsonOrange)
        embed.title = f"@{Moderation.mute_role_name} Successfully Configured  :white_check_mark:"
        await ctx.send(embed=embed)
        return True


async def setup(bot: ClemBot) -> None:
    await bot.add_cog(MuteCog(bot))
