import logging

import discord

from bot.services.base_service import BaseService
from bot.messaging.events import Events
from bot.data.moderation_repository import ModerationRepository
from bot.consts import Colors, DesignatedChannels, Moderation

log = logging.getLogger(__name__)


class ModerationService(BaseService):

    def __init__(self, *, bot):
        super().__init__(bot)

    @BaseService.Listener(Events.on_bot_ban)
    async def on_bot_ban(self, guild, author: discord.Member, subject: discord.Member, reason):
        repo = ModerationRepository()

        await guild.ban(subject, reason=reason, delete_message_days=1)

        await repo.insert_ban(guild_id=guild.id,
                              author_id=author.id,
                              subject_id=subject.id,
                              reason=reason)

    @BaseService.Listener(Events.on_bot_mute)
    async def on_bot_mute(self, guild, author: discord.Member, subject: discord.Member, reason, duration):
        repo = ModerationRepository()

        mute_role = discord.utils.get(author.guild.roles, name=Moderation.mute_role_name)
        await subject.add_roles(mute_role)

        await repo.insert_mute(guild_id=guild.id,
                               author_id=author.id,
                               subject_id=subject.id,
                               duration=duration,
                               reason=reason)

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

    async def load_service(self):
        pass
