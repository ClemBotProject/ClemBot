import logging

from bot.messaging.events import Events
from bot.services.base_service import BaseService
from bot.data.user_repository import UserRepository
import bot.messaging.messenger as messenger

log = logging.getLogger(__name__)

class UserHandling(BaseService):

    def __init__(self, *, bot):
        super().__init__(bot)

    @BaseService.Listener(Events.on_user_joined)
    async def on_user_joined(self, user) -> None:
        log.info(f'{user.name} has joined!')
        await self.add_user(user, user.guild.id)

    async def add_user(self, user, guild_id: int) -> None:
        await UserRepository().add_user(user, guild_id)

    async def load_service(self) -> None:
        for guild in self.bot.guilds:
            log.info(f'Initializing members of {guild.name}')
            for user in guild.members:
                await self.add_user(user, guild.id)
