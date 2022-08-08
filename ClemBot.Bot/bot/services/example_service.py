# import discord.py
import discord

# import a method to allow us to easily setup a logger instance with mypy not
# screaming at us (thanks seqlog)
# Import the events class so that we have all the possible events
# in the messenger defined for us clearly
from bot.clem_bot import ClemBot
from bot.messaging.events import Events

# Import the base service class so we can subclass it
# this allows the bot to load this service instance dynamically
from bot.services.base_service import BaseService
from bot.utils.logging_utils import get_logger

# get a module level logger using the __name__ of the module as the root,
# this will link it with the base logger bot. and all out put will be through that
log = get_logger(__name__)


# Services are postfixed with "Service" by convention
# They inherit from base service to allow the bot to dynamically
# reflect over the types within and load all the children of BaseService
# It also defines abstract load methods the bot depends on and handles registering
# Instance methods as messenger event callbacks
class ExampleService(BaseService):
    """
    This is an example service to demonstrate the expected layout
    A service is defined as any functionality that doesn't directly interact with a discord user
    or command, it handles background tasks and startup functionality
    """

    def __init__(self, *, bot: ClemBot):
        # The bot object that represents the current client is injected in to the service on startup and
        # Sent to the base class where it is stored
        super().__init__(bot)

    # This is the decorator for the messenger that marks a given message as a callback for an event,
    # if an event is not supplied it will default to the name of the method as the event
    @BaseService.listener(Events.on_example)
    async def on_guild_message_received(self, message: discord.Message) -> None:
        pass

    # The load service abstract method implementation defined in BaseService
    # If this method isn't added to a class that Inherits from BaseService the bot
    # won't run, even if you don't use it you still need to define it as a stub
    # all startup functionality related to this cog is started here,
    # things like updated the db  or reloading internal state
    async def load_service(self) -> None:
        pass
