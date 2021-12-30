import logging

import discord

from bot.consts import Colors, OwnerDesignatedChannels
from bot.messaging.events import Events
from bot.services.base_service import BaseService
import bot.utils.log_serializers as serializers

log = logging.getLogger(__name__)


class GuildHandlingService(BaseService):

    def __init__(self, *, bot):
        super().__init__(bot)

    @BaseService.Listener(Events.on_guild_joined)
    async def on_guild_joined(self, guild: discord.Guild) -> None:
        log.info(f'Loading guild {guild.name}: {guild.id}')

        await self._send_guild_joined_embed(guild)

        await self.bot.guild_route.add_guild(guild.id, guild.name, guild.owner.id)
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

        log.info('Guild {guild_name}: {guild_id} loaded', guild_name=guild.name, guild_id=guild.id)

        await self.bot.messenger.publish(Events.on_broadcast_designated_channel,
                                         OwnerDesignatedChannels.server_join_log,
                                         f'{guild.name}: {guild.id} initialization successful'
                                         )

    @BaseService.Listener(Events.on_guild_update)
    async def on_guild_edit(self, before: discord.Guild, after: discord.Guild):
        if before.name != after.name or before.owner.id != after.owner.id:
            await self.bot.guild_route.edit_guild(after.id, after.name, after.owner.id)

    @BaseService.Listener(Events.on_guild_leave)
    async def on_guild_leave(self, guild) -> None:
        log.info('Bot removed from {guild}', guild=serializers.log_guild(guild))

        await self.bot.messenger.publish(Events.on_broadcast_designated_channel,
                                         OwnerDesignatedChannels.server_join_log,
                                         f'Bot removed from {guild.name}: {guild.id}'
                                         )
        
        await self.bot.guild_route.leave_guild(guild.id)

    async def _send_guild_joined_embed(self, guild):

        # We arent sure what values will be there, some guilds have an odd guild object
        # Do a blanket try catch to make sure that sending the embed doesnt cause the
        # Join routines to not run if the embed throws
        try:
            embed = discord.Embed(title=f'{self.bot.user.name} added to a new guild', color=Colors.ClemsonOrange)
            embed.set_author(name=f'Owner: {guild.owner.name}#{guild.owner.discriminator}', icon_url=guild.owner.display_avatar.url)

            if guild.icon:
                embed.set_thumbnail(url=guild.icon.url)

            embed.add_field(name='Name', value=guild.name)
            embed.add_field(name='Id', value=guild.id)
            embed.add_field(name='Creation Date', value=guild.created_at, inline=False)
            embed.add_field(name='User Count', value=guild.member_count)

            await self.bot.messenger.publish(Events.on_broadcast_designated_channel,
                                             OwnerDesignatedChannels.server_join_log,
                                             embed
                                             )
        except Exception as e:
            log.error(f'Sending new guild embed failed for guild: {guild.id} with error {e}')
            await self.bot.messenger.publish(Events.on_broadcast_designated_channel,
                                             OwnerDesignatedChannels.server_join_log,
                                             f'New guild joined embed failed Guild Id: {guild.id}'
                                             )

    async def load_service(self):
        pass
