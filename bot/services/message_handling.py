
from bot.events import Events
from bot.services.base_service import BaseService
from bot.data.message_repository import MessageRepository
import bot.messaging.messenger as messenger

class MessageHandling(BaseService):

    def __init__(self):
        messenger.subscribe(Events.on_message_recieved, self.on_message_recieved)

    async def on_message_recieved(self, message) -> None:
        await MessageRepository().add_message(message)
