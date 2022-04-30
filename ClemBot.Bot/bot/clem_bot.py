import importlib
import logging
import pkgutil
import sys
import traceback
import typing as t
import datetime
from types import ModuleType

import discord
from discord.ext import commands
from discord.ext.commands import CommandNotFound

from bot.api import *
import bot.api as api
from bot.api import health_check_route
import bot.cogs as cogs
import bot.extensions as ext
import bot.services as services
import bot.bot_secrets as bot_secrets
from bot.api.api_client import ApiClient
from bot.consts import Colors
from bot.errors import ClaimsAccessError, BotOnlyRequestError
from bot.messaging.events import Events
from bot.messaging.messenger import Messenger
from bot.utils.scheduler import Scheduler
import bot.utils.log_serializers as serializers

log = logging.getLogger(__name__)


class ClemBot(commands.Bot):
    """
    This is the base level bot class for ClemBot. 

    This handles the sending of all api events
    as well as the dynamic loading of services and cogs
    """

    # noinspection PyTypeChecker
    def __init__(self, messenger, scheduler, **kwargs):
        # this super call is to pass the prefix up to the super class
        super().__init__(**kwargs)

        # Set the error callback in the messenger for queued events
        messenger.error_callback = self.global_error_handler

        # Initialize the ApiClient with callbacks and mode settings
        self.api_client = ApiClient(connect_callback=self.on_backend_connect,
                                    disconnect_callback=self.on_backend_disconnect,
                                    bot_only=bot_secrets.secrets.bot_only)

        # Bool to indicate if the bot is still in its startup procedure, if it is then
        # Dont forward events until its done
        self.is_starting_up = True

        self.messenger: Messenger = messenger
        self.scheduler: Scheduler = scheduler

        # Register our before and after invoke hooks
        self._before_invoke = self.command_claims_check
        self._after_invoke = self.on_after_command_invoke

        # pylint: disable=undefined-variable
        self.guild_route: guild_route.GuildRoute = None
        self.user_route: user_route.UserRoute = None
        self.role_route: role_route.RoleRoute = None
        self.channel_route: channel_route.ChannelRoute = None
        self.message_route: message_route.MessageRoute = None
        self.tag_route: tag_route.TagRoute = None
        self.designated_channel_route: designated_channel_route.DesignatedChannelRoute = None
        self.welcome_message_route: welcome_message_route.WelcomeMessageRoute = None
        self.custom_prefix_route: custom_prefix_route.CustomPrefixRoute = None
        self.custom_tag_prefix_route: custom_tag_prefix_route.CustomTagPrefixRoute = None
        self.moderation_route: moderation_route.ModerationRoute = None
        self.claim_route: claim_route.ClaimRoute = None
        self.commands_route: commands_route.CommandsRoute = None
        self.thread_route: thread_route.ThreadRoute = None
        self.slots_score_route: slots_score_route.SlotsScoreRoute = None
        self.health_check_route: health_check_route.HealthCheckRoute = None

        self.load_cogs()
        self.active_services = {}

        # Create a task to handle service and api startup
        self.loop.create_task(self.bot_startup())

    async def bot_startup(self):
        """
        This is the entry point of the bot that is run after discord.py has finished its startup procedures.
        This is where services are loaded and the startup procedures for each service is run
        """

        # Asynchronously wait until the api is ready for us
        await self.wait_until_ready()

        # Load the route objects into the attributes so the
        # startup service has active routes
        self.load_routes(self.api_client)

        # Connect to the api Before the services are loaded, so they can begin their startup routines
        # this will block until the api is connected to, only THEN will we run our service startups
        # until this is connected no commands will be processed because there is no message_handling_service
        # to process commands
        if not bot_secrets.secrets.bot_only:
            await self.api_client.connect()

        await self.load_services()
        log.info('Logged on as {user}', user=serializers.log_user(self.user))

    async def on_ready(self) -> None:
        embed = discord.Embed(title='Bot Started Up  :white_check_mark:', color=Colors.ClemsonOrange)
        embed.description = datetime.datetime.now().strftime("%m/%d/%Y, %H:%M")
        embed.set_author(name=f'{self.user.name}', icon_url=self.user.display_avatar.url)

        await self.send_startup_log_embed(embed)

    async def on_backend_connect(self):
        embed = discord.Embed(title='Bot Connected to ClemBot.Api  :rocket:', color=Colors.ClemsonOrange)
        embed.description = datetime.datetime.now().strftime("%m/%d/%Y, %H:%M")
        embed.set_author(name=f'{self.user.name}', icon_url=self.user.display_avatar.url)

        await self.send_startup_log_embed(embed)

    async def on_backend_disconnect(self):
        embed = discord.Embed(title='Bot Disconnected from ClemBot.Api  :warning:', color=Colors.ClemsonOrange)
        embed.description = datetime.datetime.now().strftime("%m/%d/%Y, %H:%M")
        embed.set_author(name=f'{self.user.name}', icon_url=self.user.display_avatar.url)

        await self.send_startup_log_embed(embed)

    async def close(self) -> None:
        try:
            log.info('Sending shutdown embed')
            embed = discord.Embed(title='Bot Shutting down  :no_entry_sign:', color=Colors.ClemsonOrange)
            embed.description = datetime.datetime.now().strftime("%m/%d/%Y, %H:%M")
            embed.set_author(name=f'{self.user.name}', icon_url=self.user.display_avatar.url)
            await self.send_startup_log_embed(embed)
        except Exception as e:
            log.error(f'Logout error embed failed with error {e}')

        log.info('Shutdown started: logging close time')

        await self.messenger.close()
        await super().close()

    async def send_startup_log_embed(self, embed):
        for channel_id in bot_secrets.secrets.startup_log_channel_ids:
            channel = await self.fetch_channel(channel_id)
            await channel.send(embed=embed)

    async def command_claims_check(self, ctx: commands.Context):
        """
        Before invoke hook to make sure a user has the correct claims to allow a command invocation
        """
        command = ctx.command

        if not isinstance(command, ext.ExtBase):
            # If the command isn't an extension command let it through, we dont need to think about it
            return True

        if command.ignore_claims_pre_invoke:
            # The command is going to check the claims in the command body, nothing else to do
            return

        if await self.claims_check(ctx):
            return

        await self.raise_claims_access_error(command, ctx)

    async def raise_claims_access_error(self, command, ctx):
        claims_str = '\n'.join(command.claims)
        raise ClaimsAccessError(f'Missing claims to run this operation, Need any of the following\n ```\n{claims_str}```'
                                f'\n **Help:** For more information on how claims work please visit my website [Link!]'
                                f'({bot_secrets.secrets.docs_url}/claims)\n'
                                f'or run the `{await self.current_prefix(ctx.message)}help claims` command')

    async def claims_check(self, ctx: commands.Context) -> bool:
        """
        Before cog execution to check if a user has the correct claims for aspects of a command
        """
        command = ctx.command
        author = ctx.author

        if await self.is_owner(author):
            # if the author owns the bot, authorize the command no matter what
            return True

        if author.guild_permissions.administrator:
            # Admins have full bot access no matter what
            return True

        if len(command.claims) == 0:
            # command requires no claims nothing else to do
            return True

        # Hit the db to get a users current claims
        claims = await self.claim_route.get_claims_user(author)

        if claims and command.claims_check(claims):
            # Author has valid claims
            return True
        return False

    """
    ---------------------
    Events to dispatch immediately, we do not want to queue these events as they are user facing and 
    We want the bot to respond as quickly as possible. All events dispatched inside of a command 
    context are considered instant events that skip the queue
    ---------------------
    """
    async def on_message(self, message: discord.Message) -> None:
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

    async def on_after_command_invoke(self, ctx: commands.Context):
        await self.publish_with_error(Events.on_after_command_invoke, ctx)
    """
    ----------------- End of immediate event block ---------------------
    """

    """
    Events to queue on the guild event queue, these are background service events that are 
    required for the bot to maintain its database state. These can queued and dispatched 
    in a controlled fashion
    """
    async def on_guild_join(self, guild: discord.Guild):
        await self.publish_to_queue_with_error(Events.on_guild_joined, guild.id, guild)

    async def on_guild_update(self, before: discord.Guild, after: discord.Guild):
        await self.publish_to_queue_with_error(Events.on_guild_update, before.id, before, after)

    async def on_guild_remove(self, guild: discord.Guild):
        await self.publish_to_queue_with_error(Events.on_guild_leave, guild.id, guild)

    async def on_guild_role_create(self, role: discord.Role):
        await self.publish_to_queue_with_error(Events.on_guild_role_create, role.guild.id, role)

    async def on_guild_role_update(self, before: discord.Role, after: discord.Role):
        await self.publish_to_queue_with_error(Events.on_guild_role_update, before.guild.id, before, after)

    async def on_guild_role_delete(self, role: discord.Role):
        await self.publish_to_queue_with_error(Events.on_guild_role_delete, role.guild.id, role)

    async def on_guild_channel_create(self, channel):
        await self.publish_to_queue_with_error(Events.on_guild_channel_create, channel.guild.id, channel)

    async def on_guild_channel_delete(self, channel):
        await self.publish_to_queue_with_error(Events.on_guild_channel_delete, channel.guild.id, channel)

    async def on_guild_channel_update(self, before, after):
        await self.publish_to_queue_with_error(Events.on_guild_channel_update, before.guild.id, before, after)

    async def on_thread_join(self, thread: discord.Thread):
        await self.publish_to_queue_with_error(Events.on_guild_thread_join, thread.guild.id, thread)

    async def on_thread_update(self, before: discord.Thread, after: discord.Thread):
        await self.publish_to_queue_with_error(Events.on_guild_thread_update, before.guild.id, before, after)

    async def on_member_join(self, user: discord.Member):
        await self.publish_to_queue_with_error(Events.on_user_joined, user.guild.id, user)

    async def on_member_remove(self, user: discord.Member):
        await self.publish_to_queue_with_error(Events.on_user_removed, user.guild.id, user)
    
    async def on_member_ban(self, guild: discord.Guild, user):
        await self.publish_to_queue_with_error(Events.on_member_ban, guild.id, guild, user)

    async def on_reaction_add(self, reaction: discord.Reaction, user: t.Union[discord.User, discord.Member]):
        if user.id != self.user.id:
            await self.publish_to_queue_with_error(Events.on_reaction_add, reaction.message.guild.id, reaction, user)

    async def on_raw_reaction_add(self, reaction) -> None:
        pass

    async def on_reaction_remove(self, reaction: discord.Reaction, user: t.Union[discord.User, discord.Member]):
        if user.id != self.user.id:
            await self.publish_to_queue_with_error(Events.on_reaction_remove, reaction.message.guild.id, reaction, user)

    async def on_raw_reaction_remove(self, reaction) -> None:
        pass

    async def on_member_update(self, before: discord.Member, after: discord.Member):
        await self.publish_to_queue_with_error(Events.on_member_update, before.guild.id, before, after)
    """
    ----------------- End of queued event block ---------------------
    """

    async def publish_to_queue_with_error(self, event: str, guild_id: int, *args, **kwargs):
        try:
            if not self.is_starting_up:
                await self.messenger.publish_to_queue(event, guild_id, *args, **kwargs)
        except Exception as e:
            tb = traceback.format_exc()
            await self.global_error_handler(e, traceback=tb)

    async def publish_with_error(self, event: str, *args, **kwargs):
        try:
            if not self.is_starting_up:
                await self.messenger.publish(event, *args, **kwargs)
        except Exception as e:
            tb = traceback.format_exc()
            await self.global_error_handler(e, traceback=tb)

    async def on_command_error(self, ctx, error):
        """
        Handler for cog level errors, if a command throws and isn't handled
        the exception will end up here

        Args:
            ctx ([type]): The context that the command that errored was sent from
            error ([type]): The unhandled exception
        """
        if ctx.cog:
            if commands.Cog._get_overridden_method(ctx.cog.cog_command_error) is not None:
                return
        error = getattr(error, 'original', error)

        embed = discord.Embed(title=f'ERROR: {type(error).__name__}', color=Colors.Error)
        embed.add_field(name='Exception:', value=error)
        embed.set_footer(text=self.get_full_name(ctx.author), icon_url=ctx.author.display_avatar.url)
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

        # Handle if the error is a bot only request error, this is only thrown when a request is attempted
        # In BotOnly mode so we can safely log that it happened and then ignore it
        if isinstance(e, BotOnlyRequestError):
            log.info(f'Ignoring ClemBot.Api request error in bot_only mode')
            return
        elif isinstance(e, CommandNotFound):
            log.info('Invalid command attempted: {command}', command=e.args)
            return

        # log the exception first thing so we can be sure we got it
        log.error('Unhandled Exception Thrown', exc_info=sys.exc_info())

        if traceback:
            embed = discord.Embed(title='Unhandled Exception Thrown', color=Colors.Error)
            field_length = 1000

            # this code will split the traceback into 1000 char chunks because
            # the embed will fail if we attempt to send more then that
            tb_split = [traceback[i:i + field_length] for i in range(0, len(traceback), field_length)]

            for i, field in enumerate(tb_split):
                field_name = 'Traceback' if i == 0 else 'Continued'
                embed.add_field(name=field_name, value=f'```{field}```', inline=False)

            for channel_id in bot_secrets.secrets.error_log_channel_ids:
                channel = await self.fetch_channel(channel_id)
                await channel.send(embed=embed)

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
        log.info('Loading service: {service}', service=service.__module__)

        s = service(bot=self)
        try:
            await s.load_service()
        except Exception as e:
            await self.global_error_handler(e)
        self.active_services[service.__name__] = s

    def activate_route(self, client: ApiClient, route):
        log.info('Loading route: {route}', route=route.__module__)
        r = route(api_client=client)
        # Here we remove the first 8 characters of the module name
        # That's because __module__ gives us the full name e.g bot.api.guild_route
        # so we need to remove the bot.api. to correctly set the attr name
        self.__setattr__(r.__module__[8:], r)

    async def load_services(self) -> None:
        log.info('Loading Services')
        for m in ClemBot.walk_modules('services', services):
            for s in ClemBot.walk_types(m, services.base_service.BaseService):
                if s is not services.base_service.BaseService:
                    await self.activate_service(s)

    def load_routes(self, client: ApiClient) -> None:
        log.info('Loading routes')
        for m in ClemBot.walk_modules('api', api):
            for r in ClemBot.walk_types(m, api.base_route.BaseRoute):
                if r is not api.base_route.BaseRoute:
                    self.activate_route(client, r)

    def load_cogs(self) -> None:
        log.info('Loading Cogs')
        for m in ClemBot.walk_modules('cogs', cogs):
            for c in ClemBot.walk_types(m, commands.Cog):
                log.info('Loading cog: {cog}', cog=c.__module__)
                self.load_extension(c.__module__)

    @staticmethod
    def walk_modules(module: str, pkg: t.Any) -> t.Iterator[ModuleType]:
        """Yield imported modules from the subpackage."""
        def on_error(name: str) -> t.NoReturn:
            raise ImportError(name=name)

        for _, name, ispkg in pkgutil.walk_packages(path=pkg.__path__, prefix=pkg.__name__ + '.', onerror=on_error):
            if not ispkg:
                yield importlib.import_module(name)

    @staticmethod
    def walk_types(module: ModuleType, base: t.Any) -> t.Iterator[commands.Cog]:
        """Yield all cogs defined in an extension."""
        for obj in list(module.__dict__.values()):
            # Check if it's a class type cause otherwise issubclass() may raise a TypeError.
            is_cog = isinstance(obj, type) and issubclass(obj, base)
            if is_cog and obj.__module__ == module.__name__:
                yield obj

    async def get_tag_prefix(self, ctx):
        return await self.custom_tag_prefix_route.get_custom_tag_prefixes(ctx.guild.id)
