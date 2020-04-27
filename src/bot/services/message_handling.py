from pubsub import pub as pub

from bot.events import Events
from bot.services.base_service import BaseService

class MessageHandling(BaseService):

    def __init__(self):
        pub.subscribe(self.on_message_recieved, Events.on_message_recieved)

    def on_message_recieved(self):
        a = 1
        pass

