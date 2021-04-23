# import the logging framework to allow us to log internally
# what the bot does
import logging

# Import the events class so that we have all the possible events
# in the messenger defined for us clearly
from bot.messaging.events import Events
# Import the base service class so we can subclass it
# this allows the bot to load this service instance dynamically
from bot.services.base_service import BaseService

# get a module level logger using the __name__ of the module as the root,
# this will link it with the base logger bot. and all out put will be through that
log = logging.getLogger(__name__)


# Services are postfixed with "Service" by convention
# The inherit from base service too allow the bot to dynamically
# reflect over the types within and load all of the children of BaseService
# It also defines abstract load methods the bot depends on and handles registering
# Instance methods as messenger event callbacks
class ExampleService(BaseService):
    """
    This is an example service to demonstrate the expected layout
    A service is defined as any functionality that doesnt directly interact with a discord user 
    or command, it handles background tasks and startup functionality
    """

    def __init__(self, *, bot):
        # The bot object that represents the current client is injected in to the service on startup and
        # Sent to the base class where it is stored
        super().__init__(bot)

    # This is the decorator for the messenger that marks a given message as a callback for an event,
    # if an event is not supplied it will default to the name of the method as the event
    @BaseService.Listener(Events.on_example)
    async def on_guild_message_received(self, message) -> None:
        pass

    # The load service abstract method implementation defined in BaseService
    # If this method isnt added to a class that Inherits from BaseService the bot
    # wont run, even if you dont use it you still need to define it as a stub
    # all startup functionality related to this cog is started here,
    # things like updated the db  or reloading internal state
    async def load_service(self):
        pass
