import logging
from typing import Union

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
    async def send_designated_message(self, designated_name: DesignatedChannels, content: Union[str, discord.Embed]):
        """
        Event call back to broadcast a given string or embed message to all registered designated channels

        Args:
            designated_name (DesignatedChannels): The enum name of the designated channel
            content (Union[str, discord.Embed]): The message to send
        """
        assigned_channel_ids = await DesignatedChannelRepository().get_all_assigned_channels(designated_name.name)
        if assigned_channel_ids is None:
            return

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
