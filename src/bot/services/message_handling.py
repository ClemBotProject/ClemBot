import pubsub as pub

from events import Events

class MessageHandling:

    def __init__(self):
        pub.subscribe(self.on_message_recieved, Events.on_message_recieved)


    def on_message_recieved(self):
        a = 1
        pass

