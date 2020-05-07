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
log = logging.getLogger(__name__)

class ClemBot(commands.Bot):


    def __init__(self, *args, **kwargs):
        #this super call is to pass the prefix up to the super class
        super().__init__(*args, **kwargs)

        self.load_cogs()

        self.active_services = []
        self.load_services()


    async def on_ready(self) -> None:
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

    async def on_message(self, message: str) -> None:
        log.info(f'Message from {message.author}: {message.content}')
        
        await services.message_handling.MessageHandling().on_message_recieved(message)
        await self.process_commands(message)

    async def on_guild_join(self, guild):
        pass
    
    def load_services(self) -> None:
        log.info('Loading Services')
        #self.load_extension("Cogs.manage_classes")
        for m in ClemBot.walk_modules('services', services):
            for c in ClemBot.walk_types(m, services.base_service.BaseService):
                log.info(f'Loading service: {c.__module__}')
                self.active_services.append(c())

    def load_cogs(self) -> None:
        log.info('Loading cogs')
        #self.load_extension("Cogs.manage_classes")
        for m in ClemBot.walk_modules('cogs', cogs): 
            for c in ClemBot.walk_types(m, commands.Cog):
                log.info(f'Loading Cog: {c.__module__}')
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
