import logging
from typing import Union, List

import discord

from bot.consts import DesignatedChannels
from bot.data.designated_channel_repository import DesignatedChannelRepository
from bot.messaging.events import Events
from bot.services.base_service import BaseService

log = logging.getLogger(__name__)

class DesignatedChannelService(BaseService):

    def __init__(self, *, bot):
        super().__init__(bot)

    @BaseService.Listener(Events.on_send_in_designated_channel)
    async def send_designated_message(self, 
            designated_name: DesignatedChannels, 
            guild_id: int, 
            content: Union[str, discord.Embed]):
        """
        Event call back to sent a given string or embed message to all registered designated channels
        in a given guild

        Args:
            designated_name (DesignatedChannels): The enum name of the designated channel
            content (Union[str, discord.Embed]): The message to send
        """
        dc_repo = DesignatedChannelRepository()
        assigned_channel_ids = await dc_repo.get_guild_designated_channels(designated_name.name, guild_id)

        if assigned_channel_ids is None:
            return
        
        await self._send_dc_messages(assigned_channel_ids, content)

    @BaseService.Listener(Events.on_broadcast_designated_channel)
    async def broadcast_designated_message(self, 
            designated_name: DesignatedChannels, 
            content: Union[str, discord.Embed]):
        """
        Event call back to broadcast a given string or embed message to all registered designated channels
        in all guilds

        Args:
            designated_name (DesignatedChannels): The enum name of the designated channel
            content (Union[str, discord.Embed]): The message to send
        """
        dc_repo = DesignatedChannelRepository()
        assigned_channel_ids = await dc_repo.get_all_assigned_channels(designated_name.name)

        if assigned_channel_ids is None:
            return
        
        await self._send_dc_messages(assigned_channel_ids, content)
        
    async def _send_dc_messages(self, assigned_channel_ids: List[int], content: Union[str, discord.Embed]):
        if len(assigned_channel_ids) > 0:
            for channel_id in assigned_channel_ids:
                if isinstance(content, str):
                    await self.bot.get_channel(channel_id).send(content)
                elif isinstance(content, discord.Embed):
                    await self.bot.get_channel(channel_id).send(embed= content)

    async def load_service(self):
        repo = DesignatedChannelRepository()
        for channel in DesignatedChannels:
            log.info(f'Loading designated channel: {channel.name}')
            await repo.add_designated_channel_type(channel.name)
