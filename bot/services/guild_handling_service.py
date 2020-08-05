import logging

from bot.data.guild_repository import GuildRepository
from bot.messaging.events import Events
from bot.services.base_service import BaseService

log = logging.getLogger(__name__)


class GuildHandlingService(BaseService):

    def __init__(self, *, bot):
        super().__init__(bot)

    @BaseService.Listener(Events.on_guild_joined)
    async def on_guild_joined(self, guild) -> None:
        log.info(f'Loading guild {guild.name}: {guild.id}')
        await GuildRepository().add_guild(guild)

        #The guild has been initialized, broadcast this to the rest
        #of the services
        await self.bot.messenger.publish(Events.on_new_guild_initialized, guild)
        log.info(f'Guild {guild.name}: {guild.id} loaded')

    async def add_guild(self, guild) -> None:
        await GuildRepository().add_guild(guild)

    async def load_service(self):
        for guild in self.bot.guilds:
            log.info(f'Loading guild {guild.name}: {guild.id}')
            await self.add_guild(guild)
