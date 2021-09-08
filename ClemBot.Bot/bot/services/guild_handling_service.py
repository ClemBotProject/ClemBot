import logging

import discord

from bot.consts import Colors, OwnerDesignatedChannels
from bot.messaging.events import Events
from bot.services.base_service import BaseService

log = logging.getLogger(__name__)


class GuildHandlingService(BaseService):

    def __init__(self, *, bot):
        super().__init__(bot)

    @BaseService.Listener(Events.on_guild_joined)
    async def on_guild_joined(self, guild: discord.Guild) -> None:
        log.info(f'Loading guild {guild.name}: {guild.id}')

        embed = discord.Embed(title=f'{self.bot.user.name} added to a new guild', color=Colors.ClemsonOrange)
        embed.set_author(name=f'Owner: {guild.owner.name}#{guild.owner.discriminator}', icon_url=guild.owner.display_avatar.url)
        embed.set_thumbnail(url=guild.icon.url)
        embed.add_field(name='Name', value=guild.name)
        embed.add_field(name='Id', value=guild.id)
        embed.add_field(name='Creation Date', value=guild.created_at, inline=False)
        embed.add_field(name='User Count', value=guild.member_count)

        await self.bot.messenger.publish(Events.on_broadcast_designated_channel,
                                         OwnerDesignatedChannels.server_join_log,
                                         embed
                                         )

        await self.bot.guild_route.add_guild(guild.id, guild.name)
        log.info(f'Finished Loading guild {guild.name}: {guild.id}')

        await self.bot.guild_route.update_guild_users(guild)
        log.info(f'Finished Loading guild users {guild.name}: {guild.id}')

        await self.bot.guild_route.update_guild_roles(guild)
        log.info(f'Finished Loading guild roles {guild.name}: {guild.id}')

        await self.bot.guild_route.update_guild_role_user_mappings(guild)
        log.info(f'Finished Loading guild role_user mappings {guild.name}: {guild.id}')

        # The guild has been initialized, broadcast this to the rest
        # of the services
        await self.bot.messenger.publish(Events.on_new_guild_initialized, guild)

        log.info(f'Guild {guild.name}: {guild.id} loaded')

        await self.bot.messenger.publish(Events.on_broadcast_designated_channel,
                                         OwnerDesignatedChannels.server_join_log,
                                         f'{guild.name}: {guild.id} initialization successful'
                                         )

    @BaseService.Listener(Events.on_guild_leave)
    async def on_guild_leave(self, guild) -> None:
        log.info(f'Bot removed from {guild.name}: {guild.id}')


        await self.bot.messenger.publish(Events.on_broadcast_designated_channel,
                                         OwnerDesignatedChannels.server_join_log,
                                         f'Bot removed from {guild.name}: {guild.id}'
                                         )
        
        await self.bot.guild_route.leave_guild(guild.id)


    async def load_service(self):
        pass
