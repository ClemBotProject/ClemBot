import datetime as datetime
import logging
from datetime import datetime
import typing as t
import dataclasses
import asyncio

import discord

from bot.consts import Colors, DesignatedChannels
from bot.messaging.events import Events
from bot.services.base_service import BaseService
import bot.utils.log_serializers as serializers

log = logging.getLogger(__name__)

UPDATE_EVENT_EMPTY_QUEUE_WAIT_TIME = 0.5

@dataclasses.dataclass
class UpdateEvent:
    user_id: int
    user_roles_ids: t.List[int]


class UserHandlingService(BaseService):

    def __init__(self, *, bot):
        # UserId cache so that we don't hit the database on subsequent user updates
        self.user_id_cache: t.List[int] = []

        # Guild specific user update queue to only dispatch one update event per guild at a time
        self.user_update_queue: t.Dict[int, asyncio.Queue] = {}
        super().__init__(bot)

    @BaseService.Listener(Events.on_user_joined)
    async def on_user_joined(self, user: discord.Member) -> None:
        log.info('"{member}" has joined guild "{guild}"',
                 member=serializers.log_user(user),
                 guild=serializers.log_guild(user.guild))

        db_user = await self.bot.user_route.get_user(user.id)
        if not db_user:
            await self.bot.user_route.create_user(user.id, user.name)

        await self.bot.user_route.add_user_guild(user.id, user.guild.id, raise_on_error=True)

        await self.bot.user_route.update_roles(user.id, [r.id for r in user.roles])

        await self.notify_user_join(user)

    @BaseService.Listener(Events.on_user_removed)
    async def on_user_removed(self, user) -> None:
        log.info('"{user}" has left guild "{guild}"',
                 user=serializers.log_user(user),
                 guild=serializers.log_guild(user.guild))

        # Even tho a user leaving a server doesn't clear them from the db
        # Its unlikely they are in multiple clembot servers
        # So remove them from the cache to keep its size down, and they will be
        # Readded the next time they are edited
        if user.id in self.user_id_cache:
            log.info('Removing {user} from the cache, new cache size is {size}',
                     user=serializers.log_user(user),
                     size=len(self.user_id_cache) - 1)
            self.user_id_cache.remove(user.id)

        await self.bot.user_route.remove_user_guild(user.id, user.guild.id)

        await self.notify_user_remove(user)

    @BaseService.Listener(Events.on_member_update)
    async def on_member_update(self, before: discord.Member, after: discord.Member):
        # only update roles if they have changed
        if set(r.id for r in before.roles) == set(r.id for r in after.roles):
            return

        # If user is not in local cache check the db
        if before.id not in self.user_id_cache:
            # If user is not in the db bail out
            if not await self.bot.user_route.get_user(before.id):
                # Possibly add them to the db if they don't exist
                # For future enhancement
                return

            log.info('Adding {user} to the cache, new cache size is {size}',
                     user=serializers.log_user(before),
                     size=(len(self.user_id_cache) + 1))
            # This user exists, add it to the cache
            self.user_id_cache.append(before.id)

        await self.add_to_queue(after.guild, after, [r.id for r in after.roles])

    async def add_to_queue(self, guild: discord.Guild, user: discord.Member, role_ids: t.List[int]):

        # Check if the guild_id is the in the queue dict, if it's not we need to create the queue first
        if guild.id not in self.user_update_queue:
            log.info('Creating user_update queue for guild {guild}', guild=serializers.log_guild(guild))
            self.user_update_queue[guild.id] = asyncio.Queue()

            # Create the polling task to loop over the queue and dispatch events
            asyncio.create_task(self.send_guild_queue(guild.id))

        event = UpdateEvent(user.id, role_ids)
        size = self.user_update_queue[guild.id].qsize()
        log.info('Adding UserUpdate {update_event} to {queue} with new size: {size}',
                 update_event=dataclasses.asdict(event),
                 queue=guild.id,
                 size=size+1)
        await self.user_update_queue[guild.id].put(event)

    async def send_guild_queue(self, guild_id: int):

        # Loop infinitely to dispatch events
        while True:
            try:
                # Attempt to get an enqueued event
                event = self.user_update_queue[guild_id].get_nowait()
                size = self.user_update_queue[guild_id].qsize()
            except asyncio.QueueEmpty:
                await asyncio.sleep(UPDATE_EVENT_EMPTY_QUEUE_WAIT_TIME)
                continue
                # The queue is empty we can delete it
                # log.info('Empty queue found, deleting UserUpdate Queue {queue}', queue=guild_id)
                # del self.user_update_queue[guild_id]
                # return

            log.info('Dispatching update event: {update_event} on queue: {queue} new queue size: {size}',
                     update_event=dataclasses.asdict(event),
                     queue=guild_id,
                     size=size)
            await self.bot.user_route.update_roles(event.user_id, event.user_roles_ids, raise_on_error=False)

    async def notify_user_join(self, user: discord.Member):
        embed = discord.Embed(title='New User Joined', color=Colors.ClemsonOrange)
        embed.add_field(name='Username', value=self.get_full_name(user))
        embed.add_field(name='Account Creation date', value=user.created_at.date())
        embed.set_thumbnail(url=user.display_avatar.url)
        embed.set_footer(text=str(datetime.now().date()))

        await self.bot.messenger.publish(Events.on_send_in_designated_channel,
                                         DesignatedChannels.user_join_log,
                                         user.guild.id,
                                         embed)

    async def notify_user_remove(self, user: discord.Member):
        embed = discord.Embed(title='Guild User Left', color=Colors.Error)
        embed.add_field(name='Username', value=self.get_full_name(user))
        embed.add_field(name='Account Creation date', value=user.created_at.date())
        embed.set_thumbnail(url=user.display_avatar.url)
        embed.set_footer(text=str(datetime.now().date()))

        await self.bot.messenger.publish(Events.on_send_in_designated_channel,
                                         DesignatedChannels.user_leave_log,
                                         user.guild.id,
                                         embed)

    def get_full_name(self, author) -> str:
        return f'{author.name}#{author.discriminator}'

    async def load_service(self) -> None:
        pass
