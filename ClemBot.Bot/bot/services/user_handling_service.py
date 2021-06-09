import datetime as datetime
import logging
from datetime import datetime

import discord

from bot.consts import Colors, DesignatedChannels
from bot.messaging.events import Events
from bot.services.base_service import BaseService

log = logging.getLogger(__name__)


class UserHandlingService(BaseService):

    def __init__(self, *, bot):
        super().__init__(bot)

    @BaseService.Listener(Events.on_user_joined)
    async def on_user_joined(self, user: discord.Member) -> None:
        log.info(f'"{user.name}:{user.id}" has joined guild "{user.guild.name}:{user.guild.id}"')

        db_user = await self.bot.user_route.get_user(user.id)
        if not db_user:
            await self.bot.user_route.create_user(user.id, user.name)

        await self.bot.user_route.add_user_guild(user.id, user.guild.id, raise_on_error=True)

        await self.bot.user_route.update_roles(user.id, [r.id for r in user.roles])

        await self.notify_user_join(user)

    @BaseService.Listener(Events.on_user_removed)
    async def on_user_removed(self, user) -> None:
        log.info(f'"{user.name}:{user.id}" has left guild "{user.guild.name}:{user.guild.id}"')

        await self.bot.user_route.remove_user_guild(user.id, user.guild.id)

        await self.notify_user_remove(user)

    @BaseService.Listener(Events.on_member_update)
    async def on_member_update(self, _, after):
        await self.bot.user_route.update_roles(after.id, [r.id for r in after.roles])

    async def notify_user_join(self, user: discord.Member):
        embed = discord.Embed(title='New User Joined', color=Colors.ClemsonOrange)
        embed.add_field(name='Username', value=self.get_full_name(user))
        embed.add_field(name='Account Creation date', value=user.created_at.date())
        embed.set_thumbnail(url=user.avatar_url_as(static_format='png'))
        embed.set_footer(text=str(datetime.now().date()))

        await self.bot.messenger.publish(Events.on_send_in_designated_channel,
                                         DesignatedChannels.user_join_log,
                                         user.guild.id,
                                         embed)

    async def notify_user_remove(self, user: discord.Member):
        embed = discord.Embed(title='Guild User Left', color=Colors.Error)
        embed.add_field(name='Username', value=self.get_full_name(user))
        embed.add_field(name='Account Creation date', value=user.created_at.date())
        embed.set_thumbnail(url=user.avatar_url_as(static_format='png'))
        embed.set_footer(text=str(datetime.now().date()))

        await self.bot.messenger.publish(Events.on_send_in_designated_channel,
                                         DesignatedChannels.user_leave_log,
                                         user.guild.id,
                                         embed)

    async def load_users(self, guild: discord.Guild):
        for user in guild.members:
            user_string = f'{self.get_full_name(user)}:{user.id}'
            guild_string = f'{guild.name}:{guild.id}'
            log.info(f'Loading user: {user_string} in Guild: {guild_string}')
            await self.add_user(user, guild.id)

    def get_full_name(self, author) -> str:
        return f'{author.name}#{author.discriminator}'

    async def load_service(self) -> None:
        pass
