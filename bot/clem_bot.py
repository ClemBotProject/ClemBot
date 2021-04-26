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
import bot.extensions as ext
import bot.services as services
from bot.bot_secrets import BotSecrets
from bot.consts import Colors, DesignatedChannels, OwnerDesignatedChannels
from bot.data.claims_repository import ClaimsRepository
from bot.data.database import Database
from bot.data.logout_repository import LogoutRepository
from bot.errors import ClaimsAccessError
from bot.messaging.events import Events

log = logging.getLogger(__name__)


class ClemBot(commands.Bot):
    """
    This is the base level bot class for ClemBot. 

    This handles the sending of all api events
    as well as the dynamic loading of services and cogs
    """

    def __init__(self, messenger, scheduler, **kwargs):
        # this super call is to pass the prefix up to the super class
        super().__init__(**kwargs)

        self.messenger = messenger
        self.scheduler = scheduler

        self._before_invoke = self.command_claims_check

        self.load_cogs()
        self.active_services = {}

    async def on_ready(self) -> None:
        """
        This is the entry point of the bot that is run when discord.py has finished its startup procedures.
        This is where services are loaded and the startup procedures for each service is run
        """

        await self.change_presence(activity=discord.Game(name='Run !help'))

        await Database(BotSecrets.get_instance().database_name).create_database()
        await self.load_services()

        # Send the ready event AFTER services have been loaded so that the designated channel service is there
        embed = discord.Embed(title='Bot Ready', color=Colors.ClemsonOrange)
        time = datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
        embed.add_field(name='Startup Time', value=time)
        embed.set_thumbnail(url=self.user.avatar_url)
        await self.messenger.publish(Events.on_broadcast_designated_channel, DesignatedChannels.startup_log, embed)

        log.info(f'Logged on as {self.user}')

    async def command_claims_check(self, ctx: commands.Context):
        """
        Before invoke hook to make sure a user has the correct claims to allow a command invocation
        """
        command = ctx.command
        author = ctx.author
        repo = ClaimsRepository()

        if await self.is_owner(author):
            # if the author owns the bot, authorize the command no matter what
            return

        if not isinstance(command, ext.ExtBase):
            # If the command isnt an extension command let it through, we dont need to think about it
            return

        if author.guild_permissions.administrator:
            # Admins have full bot access no matter what
            return

        if len(command.claims) == 0:
            # command requires no claims nothing else to do
            return

        if command.ignore_claims_pre_invoke:
            # The command is going to check the claims in the command body, nothing else to do
            return

        claims = await repo.fetch_all_claims_user(author)

        if claims and command.claims_check(claims):
            # Author has valid claims
            return

        claims_str = '\n'.join(command.claims)
        raise ClaimsAccessError(f'Missing claims to run this operation, Need any of the following\n ```\n{claims_str}```'
                                f'\n **Help:** For more information on how claims work please see the wiki [Link!]('
                                f'https://github.com/ClemsonCPSC-Discord/ClemBot/wiki/Authorization-Claims)\n'
                                f'or run the `{await self.current_prefix(ctx.message)}help claims` command')

    async def close(self) -> None:
        try:
            log.info('Sending shutdown embed')
            embed = discord.Embed(title='Bot Shutting down', color=Colors.ClemsonOrange)
            time = datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
            embed.add_field(name='Shutdown Time', value=time)
            embed.set_thumbnail(url=self.user.avatar_url)
            await self.messenger.publish(Events.on_broadcast_designated_channel, DesignatedChannels.startup_log, embed)
            await LogoutRepository().add_logout_date(datetime.datetime.utcnow())
        except Exception as e:
            log.error(f'Logout error embed failed with error {e}')

        log.info('Shutdown started: logging close time')
        await super().close()

    async def on_message(self, message) -> None:
        """
        Primary entry point for on_message events, all this serves to do is 
        fire that event forward on the internal message bus

        Args:
            message ([type]): The d.py message object
        """
        if message.author.id != self.user.id:
            if not isinstance(message.guild, discord.guild.Guild):
                await self.publish_with_error(Events.on_dm_message_received, message)
            else:
                await self.publish_with_error(Events.on_guild_message_received, message)

    async def on_guild_join(self, guild):
        await self.publish_with_error(Events.on_guild_joined, guild)

    async def on_guild_remove(self, guild):
        await self.publish_with_error(Events.on_guild_leave, guild)

    async def on_guild_role_create(self, role):
        await self.publish_with_error(Events.on_guild_role_create, role)

    async def on_guild_role_update(self, before, after):
        await self.publish_with_error(Events.on_guild_role_update, before, after)

    async def on_guild_role_delete(self, role):
        await self.publish_with_error(Events.on_guild_role_delete, role)

    async def on_guild_channel_create(self, channel):
        await self.publish_with_error(Events.on_guild_channel_create, channel)

    async def on_guild_channel_delete(self, channel):
        await self.publish_with_error(Events.on_guild_channel_delete, channel)

    async def on_guild_channel_update(self, before, after):
        await self.publish_with_error(Events.on_guild_channel_update, before, after)

    async def on_member_join(self, user):
        await self.publish_with_error(Events.on_user_joined, user)

    async def on_member_remove(self, user):
        await self.publish_with_error(Events.on_user_removed, user)
    
    async def on_member_ban(self, guild, user):
        await self.publish_with_error(Events.on_member_ban, guild, user)

    async def on_message_edit(self, before, after):
        if before.author.id != self.user.id and len(before.embeds) == 0:
            await self.publish_with_error(Events.on_message_edit, before, after)

    async def on_raw_message_edit(self, payload):
        # if before.author.id != self.user.id and len(before.embeds) == 0:
        if payload.cached_message is None:
            await self.publish_with_error(Events.on_raw_message_edit, payload)

    async def on_message_delete(self, message):
        if message.author.id != self.user.id:
            await self.publish_with_error(Events.on_message_delete, message)

    async def on_raw_message_delete(self, payload):
        if payload.cached_message is None:
            await self.publish_with_error(Events.on_raw_message_delete, payload)

    async def on_reaction_add(self, reaction: discord.Reaction, user: t.Union[discord.User, discord.Member]):
        if user.id != self.user.id:
            await self.publish_with_error(Events.on_reaction_add, reaction, user)

    async def on_raw_reaction_add(self, reaction) -> None:
        log.info(f'Reaction by {reaction.member.display_name} on message:{reaction.message_id}')

    async def on_reaction_remove(self, reaction: discord.Reaction, user: t.Union[discord.User, discord.Member]):
        if user.id != self.user.id:
            await self.publish_with_error(Events.on_reaction_remove, reaction, user)

    async def on_raw_reaction_remove(self, reaction) -> None:
        log.info(f'Reaction by {reaction.member.display_name} on message:{reaction.message_id}')

    async def on_member_update(self, before, after):
        await self.publish_with_error(Events.on_member_update, before, after)

    async def publish_with_error(self, *args, **kwargs):
        try:
            await self.messenger.publish(*args, **kwargs)
        except Exception as e:
            tb = traceback.format_exc()
            await self.global_error_handler(e, traceback=tb)

    async def on_command_error(self, ctx, error):
        """
        Handler for cog level errors, if a command throws and isnt handled
        the exception will end up here

        Args:
            ctx ([type]): The context that the command that errored was sent from
            e ([type]): The unhandled exception
        """
        if ctx.cog:
            if commands.Cog._get_overridden_method(ctx.cog.cog_command_error) is not None:
                return
        error = getattr(error, 'original', error)

        embed = discord.Embed(title=f'ERROR: {type(error).__name__}', color=Colors.Error)
        embed.add_field(name='Exception:', value=error)
        embed.set_footer(text=self.get_full_name(ctx.author), icon_url=ctx.author.avatar_url)
        msg = await ctx.channel.send(embed=embed)
        await self.messenger.publish(Events.on_set_deletable, msg=msg, author=ctx.author)
        await self.global_error_handler(error)

    async def global_error_handler(self, e, *, traceback: str = None):
        """
        This is the global error handler for all uncaught exceptions, if an exception is 
        thrown and not handled it will end up here. If a traceback is included in the call then
        that traceback will also be logged in a designated error channel

        Args:
            e (Error): The unhandled exception
            traceback (str) default= None: The string traceback of the throw error
        """

        # log the exception first thing so we can be sure we got it
        log.exception(e)

        if traceback:
            embed = discord.Embed(title='Unhandled Exception Thrown', color=Colors.Error)
            field_length = 1000

            # this code will split the traceback into 1000 char chunks because
            # the embed will fail if we attempt to send more then that
            tb_split = [traceback[i:i + field_length] for i in range(0, len(traceback), field_length)]

            for i, field in enumerate(tb_split):
                field_name = 'Traceback' if i == 0 else 'Continued'
                embed.add_field(name=field_name, value=f'```{field}```', inline=False)

            await self.messenger.publish(Events.on_broadcast_designated_channel, OwnerDesignatedChannels.error_log, embed)

    def get_full_name(self, author) -> str:
        return f'{author.name}#{author.discriminator}'

    async def current_prefix(self, ctx):
        prefixes = await self.get_prefix(ctx)
        return prefixes[2]

    """
    This is the code to dynamically load all cogs and services defined in the assembly.
    It reflects over itself at runtime and loads all modules that 
    inherit from the specified base class.

    This is the reason that all services and cogs must inherit from their specified
    parent type.
    """

    async def activate_service(self, service):
        log.info(f'Loading service: {service.__module__}')
        s = service(bot=self)
        try:
            await s.load_service()
        except Exception as e:
            await self.global_error_handler(e)
        self.active_services[service.__name__] = s

    async def load_services(self) -> None:
        log.info('Loading Services')
        # self.load_extension("Cogs.manage_classes")
        for m in ClemBot.walk_modules('services', services):
            for s in ClemBot.walk_types(m, services.base_service.BaseService):
                if s is not services.base_service.BaseService:
                    await self.activate_service(s)

    def load_cogs(self) -> None:
        log.info('Loading Cogs')
        # self.load_extension("Cogs.manage_classes")
        for m in ClemBot.walk_modules('cogs', cogs):
            for c in ClemBot.walk_types(m, commands.Cog):
                log.info(f'Loading cog: {c.__module__}')
                self.load_extension(c.__module__)

    @staticmethod
    def walk_modules(module: str, pkg: any) -> t.Iterator[ModuleType]:
        """Yield imported modules from the subpackage."""

        def on_error(name: str) -> t.NoReturn:
            raise ImportError(name=name)

        for _, name, ispkg in pkgutil.walk_packages(path=pkg.__path__, prefix=pkg.__name__ + '.', onerror=on_error):
            if not ispkg:
                yield importlib.import_module(name)

    @staticmethod
    def walk_types(module: ModuleType, base: any) -> t.Iterator[commands.Cog]:
        """Yield all cogs defined in an extension."""
        for obj in module.__dict__.values():
            # Check if it's a class type cause otherwise issubclass() may raise a TypeError.
            is_cog = isinstance(obj, type) and issubclass(obj, base)
            if is_cog and obj.__module__ == module.__name__:
                yield obj
