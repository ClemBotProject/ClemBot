import logging
from datetime import datetime

import discord

from bot.clem_bot import ClemBot
from bot.consts import Colors, DesignatedChannels, Moderation, Infractions
from bot.messaging.events import Events
from bot.services.base_service import BaseService
import bot.utils.log_serializers as serializers

log = logging.getLogger(__name__)


class ModerationService(BaseService):

    def __init__(self, *, bot: ClemBot):
        super().__init__(bot)

    @BaseService.Listener(Events.on_bot_warn)
    async def on_bot_warn(self, guild, author: discord.Member, subject: discord.Member, reason):
        await self.bot.moderation_route.insert_warn(guild_id=guild.id,
                                                    author_id=author.id,
                                                    subject_id=subject.id,
                                                    reason=reason,
                                                    raise_on_error=True)

    @BaseService.Listener(Events.on_bot_ban)
    async def on_bot_ban(self, guild, author: discord.Member, purge_days: int, subject: discord.Member, reason):

        await guild.ban(subject, reason=reason, delete_message_days=purge_days)

        await self.bot.moderation_route.insert_ban(guild_id=guild.id,
                                                   author_id=author.id,
                                                   subject_id=subject.id,
                                                   reason=reason,
                                                   raise_on_error=True)

    @BaseService.Listener(Events.on_bot_mute)
    async def on_bot_mute(self, guild: discord.Guild, author: discord.Member, subject: discord.Member, reason, duration):

        mute_role = discord.utils.get(author.guild.roles, name=Moderation.mute_role_name)
        await subject.add_roles(mute_role)

        mute_id = await self.bot.moderation_route.insert_mute(guild_id=guild.id,
                                                              author_id=author.id,
                                                              subject_id=subject.id,
                                                              duration=duration.strftime('%Y-%m-%dT%H:%M:%S.%f'),
                                                              reason=reason,
                                                              raise_on_error=True)

        self.bot.scheduler.schedule_at(self._unmute_callback(guild.id, subject.id, mute_id), time=duration)

    @BaseService.Listener(Events.on_bot_unmute)
    async def on_bot_unmute(self,
                            guild_id: int,
                            subject_id: int,
                            mute_id: int,
                            reason: str,
                            author: discord.Member = None):

        guild = self.bot.get_guild(guild_id)

        mute_role = discord.utils.get(guild.roles, name=Moderation.mute_role_name)

        if not author:
            author = self.bot.user

        await self.bot.moderation_route.deactivate_mute(mute_id, raise_on_error=True)

        subject = guild.get_member(subject_id)

        if not subject:
            embed = discord.Embed(color=Colors.ClemsonOrange)
            embed.title = 'Guild Member Unmuted'
            embed.add_field(name='Name unknown, member not in the server', value=f'Id: {subject_id}')
            embed.set_author(name=self.get_full_name(author), icon_url=author.display_avatar.url)
            embed.add_field(name='Reason :page_facing_up:', value=f'```{reason}```', inline=False)

            return await self.bot.messenger.publish(Events.on_send_in_designated_channel,
                                                    DesignatedChannels.moderation_log,
                                                    guild.id,
                                                    embed)

        if mute_role not in subject.roles:
            return

        await subject.remove_roles(mute_role)

        embed = discord.Embed(color=Colors.ClemsonOrange)
        embed.title = f'You have been Unmuted'
        embed.set_thumbnail(url=str(guild.icon.url))
        embed.add_field(name='Reason :page_facing_up:', value=f'```{reason}```', inline=False)
        embed.description = f'**Guild:** {guild.name}'

        try:
            await subject.send(embed=embed)
        except (discord.Forbidden, discord.HTTPException):
            embed = discord.Embed(color=Colors.ClemsonOrange)
            embed.title = f'Dm Unmute to {self.get_full_name(subject)} forbidden'
            await self.bot.messenger.publish(Events.on_send_in_designated_channel,
                                             DesignatedChannels.moderation_log,
                                             guild.id,
                                             embed)

        embed = discord.Embed(color=Colors.ClemsonOrange)
        embed.title = 'Guild Member Unmuted'
        embed.add_field(name=self.get_full_name(subject), value=f'Id: {subject.id}')
        embed.set_author(name=self.get_full_name(author), icon_url=author.display_avatar.url)
        embed.add_field(name='Reason :page_facing_up:', value=f'```{reason}```', inline=False)
        embed.set_thumbnail(url=subject.display_avatar.url)

        await self.bot.messenger.publish(Events.on_send_in_designated_channel,
                                         DesignatedChannels.moderation_log,
                                         guild.id,
                                         embed)

    @BaseService.Listener(Events.on_user_joined)
    async def on_joined(self, user: discord.Member):
        mute_role = discord.utils.get(user.guild.roles, name=Moderation.mute_role_name)

        # no mute role configured, do nothing
        if not mute_role:
            return

        mutes = await self.bot.moderation_route.get_guild_mutes_user(user.guild.id, user.id)
        mutes = [mute for mute in mutes if mute.active]

        if len(mutes) > 0:
            await user.add_roles(mute_role)
            embed = discord.Embed(color=Colors.ClemsonOrange)
            embed.title = 'Reapplied Mute'
            embed.add_field(name=self.get_full_name(user), value=f'Id: {user.id}')
            embed.add_field(name='Reason :page_facing_up:', value=f'```User left and rejoined```', inline=False)
            embed.set_thumbnail(url=user.display_avatar.url)

            await self.bot.messenger.publish(Events.on_send_in_designated_channel,
                                             DesignatedChannels.moderation_log,
                                             user.guild.id,
                                             embed)

    @BaseService.Listener(Events.on_guild_channel_create)
    async def on_channel_create(self, channel: discord.TextChannel):
        mute_role = discord.utils.get(channel.guild.roles, name=Moderation.mute_role_name)

        # no mute role configured, do nothing
        if not mute_role:
            return

        log.info('Setting mute role perms for channel: {channel} in guild {guild} ',
                 channel=serializers.log_channel(channel),
                 guild_id=serializers.log_guild(channel.guild))

        await channel.set_permissions(mute_role,
                                      speak=False,
                                      connect=False,
                                      stream=False,
                                      send_messages=False,
                                      send_messages_in_threads=False,
                                      create_public_threads=False,
                                      create_private_threads=False,
                                      send_tts_messages=False,
                                      add_reactions=False)

    @BaseService.Listener(Events.on_member_ban)
    async def on_member_ban(self, guild, user):
        log = (await guild.audit_logs(limit=1, action=discord.AuditLogAction.ban).flatten())[0]
        embed = discord.Embed(color=Colors.ClemsonOrange)
        embed.title = 'Guild Member Banned'
        embed.set_author(name=log.user, icon_url=log.user.display_avatar.url)

        #Dont send anything if clembot did the banning, we handled that case elsewhere
        if log.user == self.bot.user:
            return

        embed.add_field(name='Name', value=user.name)
        embed.add_field(name='Reason', value=log.reason)
        embed.set_thumbnail(url=user.display_avatar.url)

        await self.bot.messenger.publish(Events.on_send_in_designated_channel,
                                         DesignatedChannels.moderation_log,
                                         guild.id,
                                         embed)

    async def _unmute_callback(self, guild_id: int, user_id: int, mute_id) -> None:
        await self.bot.messenger.publish(Events.on_bot_unmute, guild_id, user_id, mute_id, 'Mute Time Expired')

    def get_full_name(self, author) -> str:
        return f'{author.name}#{author.discriminator}'

    async def load_service(self):
        for guild in self.bot.guilds:
            mutes = await self.bot.moderation_route.get_guild_infractions(guild.id)

            for mute in (m for m in mutes if m.type == Infractions.mute and m.active):
                wait: datetime = datetime.strptime(mute.duration, '%Y-%m-%dT%H:%M:%S.%f')

                if (wait - datetime.utcnow()).total_seconds() <= 0:
                    await self._unmute_callback(guild.id, mute.subject_id, mute.id)
                else:
                    self.bot.scheduler.schedule_at(self._unmute_callback(guild.id, mute.subject_id, mute.id), time=wait)
