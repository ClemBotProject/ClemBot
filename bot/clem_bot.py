import importlib
import logging
import typing as t
from types import ModuleType
import pkgutil

import discord
from discord.ext import commands

import bot.cogs as cogs
import bot.services as services
from bot.events import Events
from bot.data.database import Database
from bot.bot_secrets import BotSecrets
from bot.errors import PrimaryKeyError
import bot.messaging.messenger as messenger
log = logging.getLogger(__name__)

class ClemBot(commands.Bot):
    """
    This is the base level bot class for clem bot. this handles the sending of all api events
    as well as the dynamic loading of services and cogs
    """

    def __init__(self, *args, **kwargs):
        #this super call is to pass the prefix up to the super class
        super().__init__(*args, **kwargs)

        self.load_cogs()

        self.active_services = []
        self.load_services()

    async def on_ready(self) -> None:
        """
        This is the entry point of the bot that is run when discord.py has finished its startup procedures.
        This is where the bot checks to see if its in any new guilds and acts accordingly
        """

        await Database(BotSecrets.get_instance().database_name).create_database()

        log.info('Initializing guilds')
        for guild in self.guilds:
            try:
                await services.guild_handling.GuildHandling().add_guild(guild)
            except PrimaryKeyError as e:
                log.info(f'"{guild.name}" already known')

            log.info(f'Initializing members of {guild.name}')
            for user in guild.members:
                await services.user_handling.UserHandling().add_existing_user(user, guild.id)

        log.info(f'Logged on as {self.user}')

    async def on_message(self, message) -> None:
        try:
            log.info(f'Message from {message.author}: {message.content} in guild {message.guild.id}')
            
            await messenger.publish(Events.on_message_recieved, message)
            await self.process_commands(message)
        except Exception as e:
            log.error(e)

    async def on_guild_join(self, guild):
        pass

    async def on_raw_reaction_add(self, reaction) -> None:
        log.info(f'Reaction by {reaction.member.display_name} on message:{reaction.message_id}')
    
    def load_services(self) -> None:
        log.info('Loading Services')
        #self.load_extension("Cogs.manage_classes")
        for m in ClemBot.walk_modules('services', services):
            for c in ClemBot.walk_types(m, services.base_service.BaseService):
                log.info(f'Loading service: {c.__module__}')
                self.active_services.append(c())

    def load_cogs(self) -> None:
        log.info('Loading Cogs')
        #self.load_extension("Cogs.manage_classes")
        for m in ClemBot.walk_modules('cogs', cogs): 
            for c in ClemBot.walk_types(m, commands.Cog):
                log.info(f'Loading cog: {c.__module__}')
                self.load_extension(c.__module__)

    @staticmethod
    def walk_modules(module: str, pkg: any) -> t.Iterator[ModuleType]:
        """Yield imported modules from the subpackage."""
        def on_error(name: str) -> t.NoReturn:
            raise ImportError(name=name)

        for module in pkgutil.walk_packages(pkg.__path__, f'{module}.', onerror=on_error):
            if not module.ispkg:
                yield importlib.import_module(f'bot.{module.name}')

    @staticmethod
    def walk_types(module: ModuleType, base: any) -> t.Iterator[commands.Cog]:
        """Yield all cogs defined in an extension."""
        for obj in module.__dict__.values():
            # Check if it's a class type cause otherwise issubclass() may raise a TypeError.
            is_cog = isinstance(obj, type) and issubclass(obj, base)
            if is_cog and obj.__module__ == module.__name__:
                yield obj
