
from bot.events import Events
from bot.services.base_service import BaseService
from bot.data.message_repository import MessageRepository

class MessageHandling(BaseService):

    def __init__(self):
        pass

    async def on_message_recieved(self, message) -> None:
        await MessageRepository().add_message(message)


