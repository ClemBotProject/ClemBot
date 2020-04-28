from pubsub import pub as pub

from bot.events import Events
from bot.services.base_service import BaseService
from bot.data.message_repository import MessageRepository

class MessageHandling(BaseService):

    def __init__(self):
        pub.subscribe(self.on_message_recieved, Events.on_message_recieved)

    async def on_message_recieved(self, message) -> None:
        await MessageRepository().add_message(message)


