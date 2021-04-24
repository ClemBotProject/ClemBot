import logging
from datetime import datetime

import discord

from bot.clem_bot import ClemBot
from bot.consts import Colors, DesignatedChannels, Moderation
from bot.data.moderation_repository import ModerationRepository
from bot.messaging.events import Events
from bot.services.base_service import BaseService

log = logging.getLogger(__name__)


class ModerationService(BaseService):

    def __init__(self, *, bot: ClemBot):
        super().__init__(bot)

    @BaseService.Listener(Events.on_bot_warn)
    async def on_bot_warn(self, guild, author: discord.Member, subject: discord.Member, reason):
        repo = ModerationRepository()

        await repo.insert_warn(guild_id=guild.id,
                               author_id=author.id,
                               subject_id=subject.id,
                               reason=reason)

    @BaseService.Listener(Events.on_bot_ban)
    async def on_bot_ban(self, guild, author: discord.Member, subject: discord.Member, reason):
        repo = ModerationRepository()

        await guild.ban(subject, reason=reason, delete_message_days=1)

        await repo.insert_ban(guild_id=guild.id,
                              author_id=author.id,
                              subject_id=subject.id,
                              reason=reason)

    @BaseService.Listener(Events.on_bot_mute)
    async def on_bot_mute(self, guild: discord.Guild, author: discord.Member, subject: discord.Member, reason, duration):
        repo = ModerationRepository()

        mute_role = discord.utils.get(author.guild.roles, name=Moderation.mute_role_name)
        await subject.add_roles(mute_role)

        mute_id = await repo.insert_mute(guild_id=guild.id,
                                         author_id=author.id,
                                         subject_id=subject.id,
                                         duration=duration,
                                         reason=reason)

        self.bot.scheduler.schedule_at(self._unmute_callback(subject, mute_id), time=duration)

    @BaseService.Listener(Events.on_bot_unmute)
    async def on_bot_unmute(self, guild: discord.Guild, subject: discord.Member, mute_id, reason):
        repo = ModerationRepository()
        mute_role = discord.utils.get(guild.roles, name=Moderation.mute_role_name)

        if mute_role not in subject.roles:
            return

        await subject.remove_roles(mute_role)
        await repo.deactivate_mute(mute_id)

        embed = discord.Embed(color=Colors.ClemsonOrange)
        embed.title = f'You have been Unmuted'
        embed.set_thumbnail(url=str(guild.icon_url))
        embed.add_field(name='Reason :page_facing_up:', value=f'```{reason}```', inline=False)
        embed.description = f'**Guild:** {guild.name}'

        try:
            await subject.send(embed=embed)
        except discord.Forbidden:
            embed = discord.Embed(color=Colors.ClemsonOrange)
            embed.title = f'Dm unmute to {self.get_full_name(subject)} forbidden'
            await self.bot.messenger.publish(Events.on_send_in_designated_channel,
                                             DesignatedChannels.moderation_log,
                                             guild.id,
                                             embed)

        embed = discord.Embed(color=Colors.ClemsonOrange)
        embed.title = 'Guild Member Unmuted'
        embed.add_field(name=self.get_full_name(subject), value=f'Id: {subject.id}')
        embed.add_field(name='Reason :page_facing_up:', value=f'```{reason}```', inline=False)
        embed.set_thumbnail(url=subject.avatar_url_as(static_format='png'))

        await self.bot.messenger.publish(Events.on_send_in_designated_channel,
                                         DesignatedChannels.moderation_log,
                                         guild.id,
                                         embed)

    @BaseService.Listener(Events.on_user_joined)
    async def on_joined(self, user: discord.Member):
        repo = ModerationRepository()
        mute_role = discord.utils.get(user.guild.roles, name=Moderation.mute_role_name)

        # no mute role configured, do nothing
        if not mute_role:
            return

        mutes = await repo.get_all_active_mutes_member(user.guild.id, user.id)

        if len(mutes) > 0:
            await user.add_roles(mute_role)
            embed = discord.Embed(color=Colors.ClemsonOrange)
            embed.title = 'Reapplied Mute'
            embed.add_field(name=self.get_full_name(user), value=f'Id: {user.id}')
            embed.add_field(name='Reason :page_facing_up:', value=f'```User left and rejoined```', inline=False)
            embed.set_thumbnail(url=user.avatar_url_as(static_format='png'))

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

        log.info(f'Setting mute role perms for channel: {channel.name} in guild {channel.guild.id} ')
        await channel.set_permissions(mute_role,
                                      speak=False,
                                      connect=False,
                                      stream=False,
                                      send_messages=False,
                                      send_tts_messages=False,
                                      add_reactions=False)

    @BaseService.Listener(Events.on_member_ban)
    async def on_member_ban(self, guild, user):
        log = (await guild.audit_logs(limit=1, action=discord.AuditLogAction.ban).flatten())[0]
        embed = discord.Embed(color=Colors.ClemsonOrange)
        embed.title = 'Guild Member Banned'
        embed.set_author(name=log.user, icon_url=log.user.avatar_url)

        #Dont send anything if clembot did the banning, we handled that case elsewhere
        if log.user == self.bot.user:
            return

        embed.add_field(name='Name', value=user.name)
        embed.add_field(name='Reason', value=log.reason)
        embed.set_thumbnail(url=user.avatar_url_as(static_format='png'))

        await self.bot.messenger.publish(Events.on_send_in_designated_channel,
                                         DesignatedChannels.moderation_log,
                                         guild.id,
                                         embed)

    async def _unmute_callback(self, user: discord.Member, mute_id):
        await self.bot.messenger.publish(Events.on_bot_unmute, user.guild, user, mute_id, 'Mute Time Expired')

    def get_full_name(self, author) -> str:
        return f'{author.name}#{author.discriminator}'

    async def load_service(self):
        repo = ModerationRepository()

        for guild in self.bot.guilds:
            mutes = await repo.get_all_active_mutes(guild.id)
            for mute in mutes:
                wait: datetime = datetime.strptime(mute.duration, '%Y-%m-%d %H:%M:%S.%f')
                member = guild.get_member(mute.fk_subjectId)

                if not member:
                    continue

                if (wait - datetime.utcnow()).total_seconds() <= 0:
                    await self._unmute_callback(member, mute.id)
                else:
                    self.bot.scheduler.schedule_at(self._unmute_callback(member, mute.id), time=wait)
