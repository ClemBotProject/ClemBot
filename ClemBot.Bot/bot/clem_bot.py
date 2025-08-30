from __future__ import annotations

import datetime
import importlib
import logging
import pkgutil
import traceback
import typing as t
from types import ModuleType

import discord
from discord.ext import commands
from discord.ext.commands import CommandNotFound
from discord.ext.commands._types import BotT

import bot.bot_secrets as bot_secrets
import bot.cogs as cogs
import bot.extensions as ext
import bot.services as services
import bot.utils.log_serializers as serializers
from bot.api import (
    channel_route,
    claim_route,
    commands_route,
    custom_prefix_route,
    custom_tag_prefix_route,
    designated_channel_route,
    emote_board_route,
    guild_route,
    health_check_route,
    message_route,
    moderation_route,
    reminder_route,
    role_route,
    slots_score_route,
    tag_route,
    thread_route,
    user_route,
    welcome_message_route,
)
from bot.api.api_client import ApiClient
from bot.consts import Colors
from bot.errors import BotOnlyRequestError, SilentCommandRestrictionError
from bot.messaging.events import Events
from bot.messaging.messenger import Messenger
from bot.utils.logging_utils import get_logger
from bot.utils.scheduler import Scheduler

log = get_logger(__name__)

if t.TYPE_CHECKING:
    import bot.api.base_route as base_route
    import bot.services.base_service as base_service
    from bot.services.fuzzy_matching_service import FuzzyMatchingService


class ClemBot(commands.Bot):
    """
    This is the base level bot class for ClemBot.

    This handles the sending of all api events
    as well as the dynamic loading of services and cogs
    """

    # Override the parent user type here which is optional, we know that user won't be null
    user: discord.ClientUser

    def __init__(self, messenger: Messenger, scheduler: Scheduler, **kwargs: t.Any) -> None:
        # this super call is to pass the prefix up to the super class
        super().__init__(**kwargs)

        # Set the error callback in the messenger for queued events
        messenger.error_callback = self.global_error_handler

        # Initialize the ApiClient with callbacks and mode settings
        self.api_client = ApiClient(
            connect_callback=self.on_backend_connect,
            disconnect_callback=self.on_backend_disconnect,
            bot_only=bot_secrets.secrets.bot_only,
        )

        # Bool to indicate if the bot is still in its startup procedure, if it is then
        # Dont forward events until its done
        self.is_starting_up = True

        self.messenger: Messenger = messenger
        self.scheduler: Scheduler = scheduler

        # Register our before and after invoke hooks
        self._before_invoke = self.on_before_command_invoke
        self._after_invoke = self.on_after_command_invoke

        # pylint: disable=undefined-variable
        self.guild_route = guild_route.GuildRoute(self.api_client)
        self.user_route = user_route.UserRoute(self.api_client)
        self.role_route = role_route.RoleRoute(self.api_client)
        self.channel_route = channel_route.ChannelRoute(self.api_client)
        self.message_route = message_route.MessageRoute(self.api_client)
        self.tag_route = tag_route.TagRoute(self.api_client)
        self.designated_channel_route = designated_channel_route.DesignatedChannelRoute(
            self.api_client
        )
        self.welcome_message_route = welcome_message_route.WelcomeMessageRoute(self.api_client)
        self.custom_prefix_route = custom_prefix_route.CustomPrefixRoute(self.api_client)
        self.custom_tag_prefix_route = custom_tag_prefix_route.CustomTagPrefixRoute(self.api_client)
        self.moderation_route = moderation_route.ModerationRoute(self.api_client)
        self.claim_route = claim_route.ClaimRoute(self.api_client)
        self.commands_route = commands_route.CommandsRoute(self.api_client)
        self.thread_route = thread_route.ThreadRoute(self.api_client)
        self.slots_score_route = slots_score_route.SlotsScoreRoute(self.api_client)
        self.health_check_route = health_check_route.HealthCheckRoute(self.api_client)
        self.reminder_route = reminder_route.ReminderRoute(self.api_client)
        self.emote_board_route = emote_board_route.EmoteBoardRoute(self.api_client)

        self.active_services: dict[str, base_service.BaseService] = {}

    async def setup_hook(self) -> None:
        """
        This is the entry point of the bot that is run after discord.py has finished its startup procedures.
        This is where services are loaded and the startup procedures for each service is run
        """

        await self.load_cogs()

        # Connect to the api Before the services are loaded, so they can begin their startup routines
        # this will block until the api is connected to, only THEN will we run our service startups
        # until this is connected no commands will be processed because there is no message_handling_service
        # to process commands
        if not bot_secrets.secrets.bot_only:
            await self.api_client.connect()

        log.info("Logged on as {user}", user=serializers.log_user(self.user))

    async def on_ready(self) -> None:

        # Load the services after the gateway has connected and loaded state data into the cache
        # So that we can be sure that we correctly iterate over known guilds
        await self.load_services()

        embed = discord.Embed(
            title="Bot Started Up  :white_check_mark:", color=Colors.ClemsonOrange
        )
        embed.description = datetime.datetime.now().strftime("%m/%d/%Y, %H:%M")
        embed.set_author(name=f"{self.user.name}", icon_url=self.user.display_avatar.url)

        await self.send_startup_log_embed(embed)

    async def on_backend_connect(self) -> None:
        embed = discord.Embed(
            title="Bot Connected to ClemBot.Api  :rocket:", color=Colors.ClemsonOrange
        )
        embed.description = datetime.datetime.now().strftime("%m/%d/%Y, %H:%M")
        embed.set_author(name=f"{self.user.name}", icon_url=self.user.display_avatar.url)

        await self.send_startup_log_embed(embed)

    async def on_backend_disconnect(self) -> None:
        embed = discord.Embed(
            title="Bot Disconnected from ClemBot.Api  :warning:", color=Colors.ClemsonOrange
        )
        embed.description = datetime.datetime.now().strftime("%m/%d/%Y, %H:%M")
        embed.set_author(name=f"{self.user.name}", icon_url=self.user.display_avatar.url)

        await self.send_startup_log_embed(embed)

    async def close(self) -> None:
        try:
            log.info("Sending shutdown embed")
            embed = discord.Embed(
                title="Bot Shutting down  :no_entry_sign:", color=Colors.ClemsonOrange
            )
            embed.description = datetime.datetime.now().strftime("%m/%d/%Y, %H:%M")
            embed.set_author(name=f"{self.user.name}", icon_url=self.user.display_avatar.url)
            await self.send_startup_log_embed(embed)
        except Exception as e:
            log.error(f"Logout error embed failed with error {e}")

        log.info("Shutdown started: logging close time")

        await self.messenger.close()
        await super().close()

    async def send_startup_log_embed(self, embed: discord.Embed) -> None:
        for channel_id in bot_secrets.secrets.startup_log_channel_ids:
            channel = await self.fetch_channel(channel_id)

            if not isinstance(channel, discord.TextChannel):
                return

            await channel.send(embed=embed)

    async def on_before_command_invoke(self, ctx: ext.ClemBotCtx) -> None:
        """
        Before invoke hook to check for command restrictions & claims
        """
        await self.messenger.publish(Events.on_restrictions_check, ctx)
        await self.messenger.publish(Events.on_claims_check, ctx)

    async def claims_check(self, ctx: ext.ClemBotCtx) -> bool:
        """
        Before cog execution to check if a user has the correct claims for aspects of a command
        """
        command = ctx.command
        author = ctx.author

        if isinstance(author, discord.abc.User) and await self.is_owner(author):
            # if the author owns the bot, authorize the command no matter what
            return True

        assert isinstance(author, discord.Member)

        if author.guild_permissions.administrator:
            # Admins have full bot access no matter what
            return True

        assert command is not None

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

    async def on_message_edit(self, before: discord.Message, after: discord.Message) -> None:
        if before.author.id != self.user.id and len(before.embeds) == 0:
            await self.publish_with_error(Events.on_message_edit, before, after)

    async def on_raw_message_edit(self, payload: discord.RawMessageUpdateEvent) -> None:
        # if before.author.id != self.user.id and len(before.embeds) == 0:
        await self.publish_with_error(Events.on_raw_message_edit, payload)

    async def on_message_delete(self, message: discord.Message) -> None:
        if not message.guild:
            return
        if message.author.id != self.user.id:
            await self.publish_with_error(Events.on_message_delete, message)

    async def on_raw_message_delete(self, payload: discord.RawMessageDeleteEvent) -> None:
        if not payload.guild_id:
            return
        await self.publish_with_error(Events.on_raw_message_delete, payload)

    async def on_after_command_invoke(self, ctx: ext.ClemBotContext["ClemBot"]) -> None:
        await self.publish_with_error(Events.on_after_command_invoke, ctx)

    """
    ----------------- End of immediate event block ---------------------
    """

    """
    Events to queue on the guild event queue, these are background service events that are 
    required for the bot to maintain its database state. These can queued and dispatched 
    in a controlled fashion
    """

    async def on_guild_join(self, guild: discord.Guild) -> None:
        await self.publish_to_queue_with_error(Events.on_guild_joined, guild.id, guild)

    async def on_guild_update(self, before: discord.Guild, after: discord.Guild) -> None:
        await self.publish_to_queue_with_error(Events.on_guild_update, before.id, before, after)

    async def on_guild_remove(self, guild: discord.Guild) -> None:
        await self.publish_to_queue_with_error(Events.on_guild_leave, guild.id, guild)

    async def on_guild_role_create(self, role: discord.Role) -> None:
        await self.publish_to_queue_with_error(Events.on_guild_role_create, role.guild.id, role)

    async def on_guild_role_update(self, before: discord.Role, after: discord.Role) -> None:
        await self.publish_to_queue_with_error(
            Events.on_guild_role_update, before.guild.id, before, after
        )

    async def on_guild_role_delete(self, role: discord.Role) -> None:
        await self.publish_to_queue_with_error(Events.on_guild_role_delete, role.guild.id, role)

    async def on_guild_channel_create(self, channel: discord.abc.GuildChannel) -> None:
        await self.publish_to_queue_with_error(
            Events.on_guild_channel_create, channel.guild.id, channel
        )

    async def on_guild_channel_delete(self, channel: discord.abc.GuildChannel) -> None:
        await self.publish_to_queue_with_error(
            Events.on_guild_channel_delete, channel.guild.id, channel
        )

    async def on_guild_channel_update(
        self, before: discord.abc.GuildChannel, after: discord.abc.GuildChannel
    ) -> None:
        await self.publish_to_queue_with_error(
            Events.on_guild_channel_update, before.guild.id, before, after
        )

    async def on_thread_create(self, thread: discord.Thread) -> None:
        await self.publish_to_queue_with_error(
            Events.on_guild_thread_create, thread.guild.id, thread
        )

    async def on_thread_join(self, thread: discord.Thread) -> None:
        await self.publish_to_queue_with_error(Events.on_guild_thread_join, thread.guild.id, thread)

    async def on_thread_update(self, before: discord.Thread, after: discord.Thread) -> None:
        await self.publish_to_queue_with_error(
            Events.on_guild_thread_update, before.guild.id, before, after
        )

    async def on_member_join(self, user: discord.Member) -> None:
        await self.publish_to_queue_with_error(Events.on_initial_user_join, user.guild.id, user)

    async def on_member_remove(self, user: discord.Member) -> None:
        await self.publish_to_queue_with_error(Events.on_user_removed, user.guild.id, user)

    async def on_member_ban(self, guild: discord.Guild, user: discord.Member) -> None:
        await self.publish_to_queue_with_error(Events.on_member_ban, guild.id, guild, user)

    async def on_reaction_add(
        self, reaction: discord.Reaction, user: discord.User | discord.Member
    ) -> None:
        if user.id != self.user.id:
            assert reaction.message.guild is not None
            await self.publish_to_queue_with_error(
                Events.on_reaction_add, reaction.message.guild.id, reaction, user
            )

    async def on_raw_reaction_add(self, reaction: discord.RawReactionActionEvent) -> None:
        if reaction.user_id != self.user.id and reaction.guild_id:
            await self.publish_to_queue_with_error(
                Events.on_raw_reaction_add, reaction.guild_id, reaction
            )

    async def on_reaction_remove(
        self, reaction: discord.Reaction, user: discord.User | discord.Member
    ) -> None:
        if user.id != self.user.id:
            assert reaction.message.guild is not None
            await self.publish_to_queue_with_error(
                Events.on_reaction_remove, reaction.message.guild.id, reaction, user
            )

    async def on_raw_reaction_remove(self, reaction: discord.Reaction) -> None:
        pass

    async def on_member_update(self, before: discord.Member, after: discord.Member) -> None:
        await self.publish_to_queue_with_error(
            Events.on_member_update, before.guild.id, before, after
        )

    """
    ----------------- End of queued event block ---------------------
    """

    async def publish_to_queue_with_error(
        self, event: str, guild_id: int, *args: t.Any, **kwargs: dict[str, t.Any]
    ) -> None:
        try:
            if not self.is_starting_up:
                await self.messenger.publish_to_queue(event, guild_id, *args, **kwargs)
        except Exception as e:
            tb = traceback.format_exc()
            await self.global_error_handler(e, traceback=tb)

    async def publish_with_error(
        self, event: str, *args: t.Any, **kwargs: dict[str, t.Any]
    ) -> None:
        try:
            if not self.is_starting_up:
                await self.messenger.publish(event, *args, **kwargs)
        except Exception as e:
            tb = traceback.format_exc()
            await self.global_error_handler(e, traceback=tb)

    async def get_command_not_found_help(self, ctx: ext.ClemBotContext[BotT]) -> str | None:
        prefix = ctx.clean_prefix or await self.current_prefix(ctx)
        cmd_name = ctx.message.content.removeprefix(prefix).strip().split()[0]

        matcher = t.cast("FuzzyMatchingService", self.active_services.get("FuzzyMatchingService"))
        if not matcher:
            return None

        # attempt to fuzzy find a similar command name to suggest to them
        if (
            len(cmd_name) > 2
            and round((matcher_result := matcher.fuzzy_find_command(cmd_name)).similarity, 1) >= 0.3
        ):
            cmd = self.get_command(matcher_result.item)

            if not cmd:
                log.error(
                    "Failed to get fuzzy matched command: {command}", command=matcher_result.item
                )
                return None

            log.info(
                "Fuzzy-matched {input} to {command_name} with similarity {similarity}",
                input=cmd_name,
                command_name=cmd.qualified_name,
                similarity=matcher_result.similarity,
            )

            return f"Did you mean **`{prefix}{cmd.qualified_name}`**?"

        return None

    async def on_command_error(
        self, ctx: discord.ext.commands.Context[BotT], error: Exception
    ) -> None:
        """
        Handler for cog level errors, if a command throws and isn't handled
        the exception will end up here

        Args:
            ctx ([type]): The context that the command that errored was sent from
            error ([type]): The unhandled exception
        """

        # this is for Command Restrictions: if CommandOnCooldown is thrown
        # we want to ignore it if the command was disabled.
        if isinstance(error, discord.ext.commands.CommandOnCooldown):
            try:
                await self.messenger.publish(Events.on_restrictions_check, ctx)
            except SilentCommandRestrictionError:
                assert ctx.command is not None
                log.info(
                    "Silently ignored command {command_name} from user {user}",
                    command_name=ctx.command.qualified_name,
                    user=str(ctx.author),
                )
                return
            except Exception as e:
                # Catch and reassign any other exceptions that publishing
                # the restrictions check throws so that we can
                # report the error back to the user and log it
                error = e

        ctx = t.cast(ext.ClemBotContext[BotT], ctx)

        if ctx.cog:
            if commands.Cog._get_overridden_method(ctx.cog.cog_command_error) is not None:
                return

        error = getattr(error, "original", error)

        if isinstance(error, SilentCommandRestrictionError):  # silently ignore this
            assert ctx.command is not None
            log.info(
                "Silently ignored command {command_name} from user {user}",
                command_name=ctx.command.qualified_name,
                user=str(ctx.author),
            )
            return

        embed = discord.Embed(title=f"ERROR: {type(error).__name__}", color=Colors.Error)
        embed.set_footer(text=str(ctx.author), icon_url=ctx.author.display_avatar.url)

        if isinstance(error, CommandNotFound) and (
            help_text := await self.get_command_not_found_help(ctx)
        ):
            embed.add_field(name="Exception:", value=(str(error) + f"\n\n{help_text}"))
        else:
            embed.add_field(name="Exception:", value=error)

        msg = await ctx.channel.send(embed=embed)
        await self.messenger.publish(Events.on_set_deletable, msg=msg, author=ctx.author)

        await self.global_error_handler(error)

    async def global_error_handler(self, e: Exception, *, traceback: str | None = None) -> None:
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
            log.info("Ignoring ClemBot.Api request error in bot_only mode")
            return
        elif isinstance(e, CommandNotFound):
            log.info("Invalid command attempted: {command}", command=e.args)
            return

        # log the exception first thing so we can be sure we got it
        log.error("Unhandled Exception Thrown", exc_info=e)

        if traceback:
            embed = discord.Embed(title="Unhandled Exception Thrown", color=Colors.Error)
            field_length = 1000

            # this code will split the traceback into 1000 char chunks because
            # the embed will fail if we attempt to send more then that
            tb_split = [
                traceback[i : i + field_length] for i in range(0, len(traceback), field_length)
            ]

            for i, field in enumerate(tb_split):
                field_name = "Traceback" if i == 0 else "Continued"
                embed.add_field(name=field_name, value=f"```{field}```", inline=False)

            for channel_id in bot_secrets.secrets.error_log_channel_ids:
                channel = await self.fetch_channel(channel_id)

                if not isinstance(channel, discord.TextChannel):
                    return

                await channel.send(embed=embed)

    async def current_prefix(self, ctx: ext.ClemBotContext[BotT]) -> str:
        prefixes = await self.get_prefix(ctx.message)
        return prefixes[2]

    """
    This is the code to dynamically load all cogs and services defined in the assembly.
    It reflects over itself at runtime and loads all modules that 
    inherit from the specified base class.

    This is the reason that all services and cogs must inherit from their specified
    parent type.
    """

    async def activate_service(self, service: t.Any) -> None:
        log.info("Loading service: {service}", service=service.__module__)

        s = service(bot=self)
        try:
            await s.load_service()
        except Exception as e:
            await self.global_error_handler(e)
        self.active_services[service.__name__] = s

    async def load_services(self) -> None:
        log.info("Loading Services")
        for m in ClemBot.walk_modules("services", services):
            for s in ClemBot.walk_types(m, services.base_service.BaseService):
                if s is not services.base_service.BaseService:
                    await self.activate_service(s)

    async def load_cogs(self) -> None:
        log.info("Loading Cogs")
        for m in ClemBot.walk_modules("cogs", cogs):
            for c in ClemBot.walk_types(m, commands.Cog):
                log.info("Loading cog: {cog}", cog=c.__module__)
                await self.load_extension(c.__module__)

    @staticmethod
    def walk_modules(module: str, pkg: t.Any) -> t.Iterator[ModuleType]:
        """Yield imported modules from the subpackage."""

        def on_error(name: str) -> t.NoReturn:
            raise ImportError(name=name)

        for _, name, ispkg in pkgutil.walk_packages(
            path=pkg.__path__, prefix=pkg.__name__ + ".", onerror=on_error
        ):
            if not ispkg:
                yield importlib.import_module(name)

    @staticmethod
    def walk_types(module: ModuleType, base: t.Any) -> t.Iterator[t.Any]:
        """Yield all cogs defined in an extension."""
        for obj in list(module.__dict__.values()):
            # Check if it's a class type cause otherwise issubclass() may raise a TypeError.
            is_cog = isinstance(obj, type) and issubclass(obj, base)
            if is_cog and obj.__module__ == module.__name__:
                yield obj

    async def get_tag_prefix(self, ctx: ext.ClemBotCtx) -> list[str]:
        assert ctx.guild is not None
        return await self.custom_tag_prefix_route.get_custom_tag_prefixes(ctx.guild.id)
