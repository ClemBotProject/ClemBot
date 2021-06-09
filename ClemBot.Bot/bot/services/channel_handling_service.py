import logging

import discord

from bot.messaging.events import Events
from bot.services.base_service import BaseService

log = logging.getLogger(__name__)


class ChannelHandlingService(BaseService):

    def __init__(self, *, bot):
        super().__init__(bot)

    @BaseService.Listener(Events.on_guild_channel_create)
    async def channel_create(self, channel):
        log.info(f'New channel created {channel.name}:{channel.id} in guild: {channel.guild.name}:{channel.guild.id}')
        await self.bot.channel_route.create_channel(channel.id, channel.name, channel.guild.id, raise_on_error=True)

    @BaseService.Listener(Events.on_guild_channel_delete)
    async def channel_delete(self, channel):
        log.info(f'Channel deleted {channel.name}:{channel.id} in guild: {channel.guild.name}:{channel.guild.id}')
        await self.bot.channel_route.remove_channel(channel.id, raise_on_error=True)

    @BaseService.Listener(Events.on_new_guild_initialized)
    async def on_new_guild_init(self, guild: discord.Guild):
        await self.bot.guild_route.update_guild_channels(guild.id, guild.channels)

    @BaseService.Listener(Events.on_guild_channel_update)
    async def channel_update(self, before, after):
        await self.bot.channel_route.edit_channel(after.id, after.name, raise_on_error=True)

    async def load_service(self):
        pass
