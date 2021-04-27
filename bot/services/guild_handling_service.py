import logging

import discord

from bot.consts import Colors, OwnerDesignatedChannels
from bot.data.guild_repository import GuildRepository
from bot.messaging.events import Events
from bot.services.base_service import BaseService

log = logging.getLogger(__name__)


class GuildHandlingService(BaseService):

    def __init__(self, *, bot):
        super().__init__(bot)

    @BaseService.Listener(Events.on_guild_joined)
    async def on_guild_joined(self, guild: discord.Guild) -> None:
        log.info(f'Loading guild {guild.name}: {guild.id}')

        await GuildRepository().add_guild(guild)

        # The guild has been initialized, broadcast this to the rest
        # of the services
        await self.bot.messenger.publish(Events.on_new_guild_initialized, guild)
        log.info(f'Guild {guild.name}: {guild.id} loaded')

        embed = discord.Embed(title=f'{self.bot.user.name} added to a new guild', color=Colors.ClemsonOrange)
        embed.set_author(name=f'Owner: {guild.owner.name}#{guild.owner.discriminator}', icon_url=guild.owner.avatar_url)
        embed.set_thumbnail(url=guild.icon_url)
        embed.add_field(name='Name', value=guild.name)
        embed.add_field(name='Id', value=guild.id)
        embed.add_field(name='Creation Date', value=guild.created_at, inline=False)
        embed.add_field(name='User Count', value=guild.member_count)

        await self.bot.messenger.publish(Events.on_broadcast_designated_channel,
                                         OwnerDesignatedChannels.server_join_log,
                                         embed
                                         )

    @BaseService.Listener(Events.on_guild_leave)
    async def on_guild_leave(self, guild) -> None:
        log.info(f'Bot removed from {guild.name}: {guild.id}')
        await GuildRepository().set_guild_status(guild.id, False)

        await self.bot.messenger.publish(Events.on_broadcast_designated_channel,
                                         OwnerDesignatedChannels.server_join_log,
                                         f'Bot removed from {guild.name}: {guild.id}'
                                         )

    async def add_guild(self, guild) -> None:
        await GuildRepository().add_guild(guild)

    async def load_service(self):
        guild_repo = GuildRepository()

        db_guilds = await guild_repo.get_all_guilds_ids()
        api_guilds = [r.id for r in self.bot.guilds]

        for removed_id in set(db_guilds) - set(api_guilds):
            log.info(f'Guild {removed_id} removed from active servers')
            await guild_repo.set_guild_status(removed_id, False)

        for guild in self.bot.guilds:
            log.info(f'Loading guild {guild.name}: {guild.id}')
            await self.add_guild(guild)
