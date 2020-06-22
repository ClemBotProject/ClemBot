import logging

from bot.messaging.events import Events
from bot.services.base_service import BaseService
from bot.data.message_repository import MessageRepository
import bot.messaging.messenger as messenger

log = logging.getLogger(__name__)

class MessageHandling(BaseService):

    def __init__(self, *, bot):
        super().__init__(bot)

    @BaseService.Listener(Events.on_message_recieved)
    async def on_message_recieved(self, message) -> None:
        log.info(f'Message from {message.author}: {message.content} in guild {message.guild.id}')

        if self.bot.user.mentioned_in(message) and message.mention_everyone is False:
            await message.channel.send('Hello there everyone!!')
        
        await self.bot.process_commands(message)
        await MessageRepository().add_message(message)

    async def load_service(self):
        pass
