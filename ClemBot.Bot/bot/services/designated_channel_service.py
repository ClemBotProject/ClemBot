import uuid
from typing import List, Optional, Union

import discord

from bot.clem_bot import ClemBot
from bot.consts import DesignatedChannelBase, DesignatedChannels
from bot.messaging.events import Events
from bot.services.base_service import BaseService
from bot.utils.logging_utils import get_logger

log = get_logger(__name__)


class DesignatedChannelService(BaseService):
    def __init__(self, *, bot: ClemBot):
        super().__init__(bot)

    @BaseService.listener(Events.on_send_in_designated_channel)
    async def send_designated_message(
        self,
        designated_name: DesignatedChannelBase,
        guild_id: int,
        content: str | discord.Embed,
        dc_id: int | uuid.UUID | None = None,
    ) -> None:
        """
        Event call back to sent a given string or embed message to all registered designated channels
        in a given guild

        Args:
            designated_name (DesignatedChannels): The enum name of the designated channel
            guild_id (int): the guild to send the message in
            content (Union[str, discord.Embed]): The message to send
            dc_id [optional] (int) an optional callback id to associate sent dc messages at the publish site
        """
        assigned_channel_ids = (
            await self.bot.designated_channel_route.get_guild_designated_channel_ids(
                guild_id, designated_name.name
            )
        )

        if assigned_channel_ids is None:
            return

        sent_messages = await self._send_dc_messages(assigned_channel_ids, content)

        if dc_id:
            await self.messenger.publish(Events.on_designated_message_sent, dc_id, sent_messages)

    @BaseService.listener(Events.on_broadcast_designated_channel)
    async def broadcast_designated_message(
        self, designated_name: DesignatedChannels, content: str | discord.Embed
    ) -> None:
        """
        Event call back to broadcast a given string or embed message to all registered designated channels
        in all guilds

        Args:
            designated_name (DesignatedChannels): The enum name of the designated channel
            content (Union[str, discord.Embed]): The message to send
        """
        assigned_channel_ids = await self.bot.designated_channel_route.get_global_designations(
            designated_name.name
        )

        if assigned_channel_ids is None:
            return

        await self._send_dc_messages(assigned_channel_ids, content)

    async def _send_dc_messages(
        self, assigned_channel_ids: List[int], content: Union[str, discord.Embed]
    ) -> List[discord.Message]:
        sent_messages = []

        if len(assigned_channel_ids) > 0:
            for channel_id in assigned_channel_ids:
                channel = self.bot.get_channel(channel_id)
                assert isinstance(channel, discord.TextChannel)

                if isinstance(content, str):
                    mes = await channel.send(content)
                    sent_messages.append(mes)
                elif isinstance(content, discord.Embed):
                    mes = await channel.send(embed=content)
                    sent_messages.append(mes)

        return sent_messages

    async def load_service(self) -> None:
        pass
