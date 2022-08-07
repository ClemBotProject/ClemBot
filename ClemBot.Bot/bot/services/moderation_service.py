from datetime import datetime
import typing as t

import discord

import bot.utils.log_serializers as serializers
from bot.clem_bot import ClemBot
from bot.utils.helpers import parse_datetime, format_datetime
from bot.consts import Colors, DesignatedChannels, Infractions, Moderation
from bot.messaging.events import Events
from bot.services.base_service import BaseService
from bot.utils.logging_utils import get_logger

log = get_logger(__name__)


class ModerationService(BaseService):
    def __init__(self, *, bot: ClemBot):
        super().__init__(bot)

    @BaseService.listener(Events.on_bot_warn)
    async def on_bot_warn(self, guild: discord.Guild, author: discord.Member, subject: discord.Member, reason: t.Optional[str]) -> None:
        await self.bot.moderation_route.insert_warn(
            guild_id=guild.id,
            author_id=author.id,
            subject_id=subject.id,
            reason=reason,
            raise_on_error=True,
        )

    @BaseService.listener(Events.on_bot_ban)
    async def on_bot_ban(
        self, guild: discord.Guild, author: discord.Member, purge_days: int, subject: discord.Member, reason: t.Optional[str]
    ) -> None:
        await guild.ban(t.cast(discord.abc.Snowflake, subject), reason=reason, delete_message_days=purge_days)

        await self.bot.moderation_route.insert_ban(
            guild_id=guild.id,
            author_id=author.id,
            subject_id=subject.id,
            reason=reason,
            raise_on_error=True,
        )

    @BaseService.listener(Events.on_bot_mute)
    async def on_bot_mute(
        self,
        guild: discord.Guild,
        author: discord.Member,
        subject: discord.Member,
        reason: t.Optional[str],
        duration: datetime,
    ) -> None:

        mute_role = discord.utils.get(author.guild.roles, name=Moderation.mute_role_name)
        assert mute_role is not None
        await subject.add_roles(t.cast(discord.abc.Snowflake, mute_role))

        mute_id = await self.bot.moderation_route.insert_mute(guild_id=guild.id,
                                                              author_id=author.id,
                                                              subject_id=subject.id,
                                                              duration=format_datetime(duration),
                                                              reason=reason,
                                                              raise_on_error=True)

        self.bot.scheduler.schedule_at(
            self._unmute_callback(guild.id, subject.id, mute_id), time=duration
        )

    @BaseService.listener(Events.on_bot_unmute)
    async def on_bot_unmute(
        self,
        guild_id: int,
        subject_id: int,
        mute_id: int,
        reason: str,
        author: t.Optional[discord.Member] = None,
    ) -> None:

        guild = self.bot.get_guild(guild_id)

        assert guild is not None

        mute_role = discord.utils.get(guild.roles, name=Moderation.mute_role_name)

        assert mute_role is not None

        if not author:
            author = guild.me
        
        assert author is not None

        mute = await self.bot.moderation_route.get_infraction(mute_id)

        if not mute.active:
            # This mute was manually removed, we can ignore it
            return

        await self.bot.moderation_route.deactivate_mute(mute_id, raise_on_error=True)

        subject = guild.get_member(subject_id)

        if not subject:
            embed = discord.Embed(color=Colors.ClemsonOrange)
            embed.title = "Guild Member Unmuted"
            embed.add_field(
                name="Name unknown, member not in the server", value=f"Id: {subject_id}"
            )
            embed.set_author(name=str(author), icon_url=author.display_avatar.url)
            embed.add_field(name="Reason :page_facing_up:", value=f"```{reason}```", inline=False)

            return await self.bot.messenger.publish(
                Events.on_send_in_designated_channel,
                DesignatedChannels.moderation_log,
                guild.id,
                embed,
            )

        if mute_role not in subject.roles:
            return

        await subject.remove_roles(t.cast(discord.abc.Snowflake, mute_role))

        embed = discord.Embed(color=Colors.ClemsonOrange)
        embed.title = "You have been Unmuted"
        embed.set_thumbnail(url=str(guild.icon))
        embed.add_field(name="Reason :page_facing_up:", value=f"```{reason}```", inline=False)
        embed.description = f"**Guild:** {guild}"

        try:
            await subject.send(embed=embed)
        except (discord.Forbidden, discord.HTTPException):
            embed = discord.Embed(color=Colors.ClemsonOrange)
            embed.title = f"Dm Unmute to {subject} forbidden"
            await self.bot.messenger.publish(
                Events.on_send_in_designated_channel,
                DesignatedChannels.moderation_log,
                guild.id,
                embed,
            )

        embed = discord.Embed(color=Colors.ClemsonOrange)
        embed.title = "Guild Member Unmuted"
        embed.add_field(name=str(subject), value=f"Id: {subject.id}")
        embed.set_author(name=str(author), icon_url=author.display_avatar.url)
        embed.add_field(name="Reason :page_facing_up:", value=f"```{reason}```", inline=False)
        embed.set_thumbnail(url=subject.display_avatar.url)

        await self.bot.messenger.publish(
            Events.on_send_in_designated_channel, DesignatedChannels.moderation_log, guild.id, embed
        )

    @BaseService.listener(Events.on_user_joined)
    async def on_joined(self, user: discord.Member) -> None:
        mute_role = discord.utils.get(user.guild.roles, name=Moderation.mute_role_name)

        # no mute role configured, do nothing
        if not mute_role:
            return

        mutes = await self.bot.moderation_route.get_guild_mutes_user(user.guild.id, user.id)
        mutes = [mute for mute in mutes if mute.active]

        if len(mutes) > 0:
            await user.add_roles(t.cast(discord.abc.Snowflake, mute_role))
            embed = discord.Embed(color=Colors.ClemsonOrange)
            embed.title = "Reapplied Mute"
            embed.add_field(name=str(user), value=f"Id: {user.id}")
            embed.add_field(
                name="Reason :page_facing_up:", value="```User left and rejoined```", inline=False
            )
            embed.set_thumbnail(url=user.display_avatar.url)

            await self.bot.messenger.publish(
                Events.on_send_in_designated_channel,
                DesignatedChannels.moderation_log,
                user.guild.id,
                embed,
            )

    @BaseService.listener(Events.on_guild_channel_create)
    async def on_channel_create(self, channel: discord.TextChannel) -> None:
        mute_role = discord.utils.get(channel.guild.roles, name=Moderation.mute_role_name)

        # no mute role configured, do nothing
        if not mute_role:
            return

        log.info(
            "Setting mute role perms for channel: {channel} in guild {guild} ",
            channel=serializers.log_channel(channel),
            guild_id=serializers.log_guild(channel.guild),
        )

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

    @BaseService.listener(Events.on_member_ban)
    async def on_member_ban(self, guild: discord.Guild, user: discord.Member) -> None:
        log = [action async for action in guild.audit_logs(limit=1, action=discord.AuditLogAction.ban)][0]
        embed = discord.Embed(color=Colors.ClemsonOrange)
        embed.title = "Guild Member Banned"

        assert log.user is not None

        embed.set_author(name=log.user, icon_url=log.user.display_avatar.url)

        # Don't send anything if clembot did the banning, we handled that case elsewhere
        if log.user == self.bot.user:
            return

        embed.add_field(name="Name", value=user.name)
        embed.add_field(name="Reason", value=log.reason)
        embed.set_thumbnail(url=user.display_avatar.url)

        await self.bot.messenger.publish(
            Events.on_send_in_designated_channel, DesignatedChannels.moderation_log, guild.id, embed
        )

    async def _unmute_callback(self, guild_id: int, user_id: int, mute_id: int) -> None:
        await self.bot.messenger.publish(
            Events.on_bot_unmute, guild_id, user_id, mute_id, "Mute Time Expired"
        )

    async def load_service(self) -> None:
        for guild in self.bot.guilds:
            mutes = await self.bot.moderation_route.get_guild_infractions(guild.id)

            for mute in (m for m in mutes if m.type == Infractions.mute and m.active):
                wait = parse_datetime(mute.duration)

                if (wait - datetime.utcnow()).total_seconds() <= 0:
                    await self._unmute_callback(guild.id, mute.subject_id, mute.id)
                else:
                    self.bot.scheduler.schedule_at(
                        self._unmute_callback(guild.id, mute.subject_id, mute.id), time=wait
                    )
