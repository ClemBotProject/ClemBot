import discord
import importlib
import typing as t
from types import ModuleType
import pkgutil
from bot import cogs
from discord.ext import commands
import logging
log = logging.getLogger(__name__)

class ClemBot(commands.Bot):

    def __init__(self, *args, **kwargs):
        #this super call is to pass the prefix up to the super class
        super().__init__(*args, **kwargs)
        self.load_cogs()

    async def on_ready(self) -> None:
        log.info(f'Logged on as {self.user}')

    async def on_message(self, message: str) -> None:
        log.info(f'Message from {message.author}: {message.content}')
        await self.process_commands(message)

    def load_cogs(self) -> None:
        log.info('Loading cogs')
        #self.load_extension("Bot.Cogs.manage_classes")
        for m in ClemBot.walk_modules():
            for c in ClemBot.walk_cogs(m):
                self.load_extension(c.__module__)

    @staticmethod
    def walk_modules() -> t.Iterator[ModuleType]:
        """Yield imported modules from the bot.cogs subpackage."""
        def on_error(name: str) -> t.NoReturn:
            raise ImportError(name=name)

        for module in pkgutil.walk_packages(cogs.__path__, "bot.cogs.", onerror=on_error):
            if not module.ispkg:
                yield importlib.import_module(module.name)

    @staticmethod
    def walk_cogs(module: ModuleType) -> t.Iterator[commands.Cog]:
        """Yield all cogs defined in an extension."""
        for obj in module.__dict__.values():
            # Check if it's a class type cause otherwise issubclass() may raise a TypeError.
            is_cog = isinstance(obj, type) and issubclass(obj, commands.Cog)
            if is_cog and obj.__module__ == module.__name__:
                yield obj

