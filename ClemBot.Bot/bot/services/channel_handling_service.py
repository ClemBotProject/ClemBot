import logging

import discord

from bot.messaging.events import Events
from bot.services.base_service import BaseService
import bot.utils.log_serializers as serializers

log = logging.getLogger(__name__)


class ChannelHandlingService(BaseService):

    def __init__(self, *, bot):
        super().__init__(bot)

    @BaseService.Listener(Events.on_guild_channel_create)
    async def channel_create(self, channel):
        log.info('Channel created {channel} in guild: {guild}',
                 channel=serializers.log_channel(channel),
                 guild=serializers.log_guild(channel.guild))

        await self.bot.channel_route.create_channel(channel.id, channel.name, channel.guild.id, raise_on_error=True)

    @BaseService.Listener(Events.on_guild_channel_delete)
    async def channel_delete(self, channel):
        log.info('Channel deleted {channel} in guild: {guild}',
                 channel=serializers.log_channel(channel),
                 guild=serializers.log_guild(channel.guild))

        await self.bot.channel_route.remove_channel(channel.id, raise_on_error=True)

    @BaseService.Listener(Events.on_new_guild_initialized)
    async def on_new_guild_init(self, guild: discord.Guild):
        await self.bot.guild_route.update_guild_channels(guild)

    @BaseService.Listener(Events.on_guild_channel_update)
    async def channel_update(self, before: discord.TextChannel, after: discord.TextChannel):
        if before.name != after.name:
            await self.bot.channel_route.edit_channel(after.id, after.name, raise_on_error=True)

    async def load_service(self):
        pass
