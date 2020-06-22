import logging

from bot.messaging.events import Events
from bot.services.base_service import BaseService
from bot.data.role_repository import RoleRepository
from bot.messaging import messenger
log = logging.getLogger(__name__)

class RoleHandling(BaseService):

    def __init__(self, *, bot):
        super().__init__(bot)

    @BaseService.Listener(Events.on_guild_role_create)
    async def on_role_create(self, role):
        pass

    @BaseService.Listener(Events.on_guild_role_delete)
    async def on_role_delete(self, role):
        pass

    @BaseService.Listener(Events.on_guild_role_update)
    async def on_role_update(self, role):
        pass

    async def load_service(self):
        for guild in self.bot.guilds:
            for role in guild.roles:
                log.info(f'Loading role "{role.name}" in {guild.name}')
                await RoleRepository().add_role(role, guild.id)
