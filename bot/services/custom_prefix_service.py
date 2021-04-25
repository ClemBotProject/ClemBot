import logging

from bot.data.custom_prefixes_repository import CustomPrefixesRepository
from bot.messaging.events import Events
from bot.services.base_service import BaseService

log = logging.getLogger(__name__)


class GuildHandlingService(BaseService):

    def __init__(self, *, bot):
        super().__init__(bot)

    # this only supports one prefix per guild atm, can be easily swapped to support more per guild
    async def load_service(self):
        repo = CustomPrefixesRepository()
        for guild in self.bot.guilds:
            log.info(f'Loading guild prefix {guild.name}: {guild.id}')
            prefix = await repo.get_prefix(guild.id)
            if prefix:
                await self.bot.messenger.publish(Events.on_set_custom_prefix, guild, prefix[0])
