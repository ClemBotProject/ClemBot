import logging

import discord

from bot.messaging.events import Events
from bot.services.base_service import BaseService
import bot.utils.log_serializers as serializers

log = logging.getLogger(__name__)


class ThreadHandlingService(BaseService):

    def __init__(self, *, bot):
        super().__init__(bot)

    @BaseService.Listener(Events.on_guild_thread_join)
    async def thread_join(self, thread: discord.Thread):

        # This event fires whenever the bot joins a thread and when a thread is created
        # Check if the thread already exists in the db and if it does do nothing else
        if await self.bot.thread_route.get_thread(thread.id):
            return

        log.info('New thread joined {thread_name}:{thread_id} in guild: {guild}',
                 thread_name=thread.name,
                 thread_id=thread.id,
                 guild=serializers.log_guild(thread.guild))

        await self.bot.thread_route.create_thread(thread.id,
                                                  thread.name,
                                                  thread.guild.id,
                                                  thread.parent_id,
                                                  raise_on_error=True)

    @BaseService.Listener(Events.on_new_guild_initialized)
    async def on_new_guild_init(self, guild: discord.Guild):
        await self.bot.guild_route.update_guild_threads(guild)

    @BaseService.Listener(Events.on_guild_thread_update)
    async def thread_update(self, before: discord.Thread, after: discord.Thread):
        if before.name != after.name:
            await self.bot.thread_route.edit_thread(after.id, after.name, raise_on_error=True)

    async def load_service(self):
        pass
