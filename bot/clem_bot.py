import datetime
import importlib
import logging
import pkgutil
import traceback
import typing as t
from types import ModuleType

import discord
from discord.ext import commands

import bot.cogs as cogs
import bot.messaging.messenger as messenger
import bot.services as services
from bot.bot_secrets import BotSecrets
from bot.consts import Colors, DesignatedChannels
from bot.data.database import Database
from bot.data.logout_repository import LogoutRepository
from bot.messaging.events import Events

log = logging.getLogger(__name__)

class ClemBot(commands.Bot):
    """
    This is the base level bot class for ClemBot. this handles the sending of all api events
    as well as the dynamic loading of services and cogs
    """

    def __init__(self, *args, **kwargs):
        #this super call is to pass the prefix up to the super class
        super().__init__(*args, **kwargs)

        self.load_cogs()
        self.active_services = {}

    async def on_ready(self) -> None:
        """
        This is the entry point of the bot that is run when discord.py has finished its startup procedures.
        This is where services are loaded and the startup procedures for each service is run
        """

        await Database(BotSecrets.get_instance().database_name).create_database()
        await self.load_services()

        #Send the ready event AFTER services have been loaded so that the designated channel service is there
        embed = discord.Embed(title='Bot Ready', color= Colors.ClemsonOrange)
        embed.add_field(name= 'Startup Time', value= datetime.datetime.utcnow())
        embed.set_thumbnail(url= self.user.avatar_url)
        await messenger.publish(Events.on_send_in_designated_channel, DesignatedChannels.startup_log, embed)

        log.info(f'Logged on as {self.user}')

    async def close(self) -> None:
        embed = discord.Embed(title='Bot Shutting down', color= Colors.ClemsonOrange)
        embed.add_field(name= 'Shutdown Time', value= datetime.datetime.utcnow())
        embed.set_thumbnail(url= self.user.avatar_url)
        await messenger.publish(Events.on_send_in_designated_channel, DesignatedChannels.startup_log, embed)

        log.info('Shutdown started: logging close time')
        await LogoutRepository().add_logout_date(datetime.datetime.utcnow())
        await super().close()

    async def on_message(self, message) -> None:
        """
        Primary entry point for on_message events, all this serves to do is 
        fire that event forward on the internal message bus

        Args:
            message ([type]): The d.py message object
        """

        if message.author.id != self.user.id:
            await self.publish_with_error(Events.on_message_recieved, message)

    async def on_guild_join(self, guild):
        await self.publish_with_error(Events.on_guild_joined, guild)

    async def on_guild_role_create(self, role):
        await self.publish_with_error(Events.on_guild_role_create, role)

    async def on_guild_role_update(self, before, after):
        await self.publish_with_error(Events.on_guild_role_update, before, after)

    async def on_guild_role_delete(self, role):
        await self.publish_with_error(Events.on_guild_role_delete, role)

    async def on_message_edit(self, before, after):
        if before.author.id != self.user.id and len(before.embeds) == 0:
            await self.publish_with_error(Events.on_message_edit, before, after)
    
    async def on_message_delete(self, message):
        if message.author.id != self.user.id:
            await self.publish_with_error(Events.on_message_delete, message)
        
    async def publish_with_error(self, *args, **kwargs):
        try:
            await messenger.publish(*args, **kwargs)
        except Exception as e:
            tb = traceback.format_exc()
            await self.global_error_handler(e, traceback= tb)

    async def on_command_error(self, ctx, e):
        """
        Handler for cog level errors, if a command throws and isnt handled
        the exception will end up here

        Args:
            ctx ([type]): The context that the command that errored was sent from
            e ([type]): The unhandled exception
        """

        embed = discord.Embed(title="ERROR: Command exception", color=Colors.Error)
        embed.add_field(name=ctx.author, value= e)
        await ctx.channel.send(embed= embed)
        await self.global_error_handler(e)

    async def on_raw_reaction_add(self, reaction) -> None:
        log.info(f'Reaction by {reaction.member.display_name} on message:{reaction.message_id}')

    async def global_error_handler(self, e, *, traceback: str = None):
        """
        This is the global error handler for all uncaught exceptions, if an exception is 
        thrown and not handled it will end up here. If a traceback is included in the call then
        that traceback will also be logged in a designated error channel

        Args:
            e (Error): The unhandled exception
            traceback (str) default= None: The string traceback of the throw error
        """        

        #log the exception first thing so we can be sure we got it
        log.exception(e)

        if traceback:
            embed = discord.Embed(title= 'Unhandled Exception Thrown', color= Colors.Error)
            field_length = 1000

            #this code will split the traceback into 1000 char chunks because 
            # the embed will fail if we attempt to send more then that
            tb_split = [traceback[i:i + field_length] for i in range(0, len(traceback), field_length)]

            for i, field in enumerate(tb_split):
                field_name = 'Traceback' if i == 0 else 'Continued'
                embed.add_field(name= field_name, value= f'```{field}```', inline= False)

            await messenger.publish(Events.on_send_in_designated_channel, DesignatedChannels.error_log, embed)

    """
    This is the code to dynamically load all cogs and services defined in the assembly.
    It reflects over itself at runtime and loads all modules that 
    inherit from the specified base class.

    This is the reason that all services and cogs must inherit from their specified
    parent type.
    """
    async def activate_service(self, service):
        log.info(f'Loading service: {service.__module__}') 
        s = service(bot= self)
        try:
            await s.load_service()
        except Exception as e:
            await self.global_error_handler(e)
        self.active_services[service.__name__] = s
    
    async def load_services(self) -> None:
        log.info('Loading Services')
        #self.load_extension("Cogs.manage_classes")
        for m in ClemBot.walk_modules('services', services):
            for s in ClemBot.walk_types(m, services.base_service.BaseService):
                if s is not services.base_service.BaseService:
                    await self.activate_service(s)

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
