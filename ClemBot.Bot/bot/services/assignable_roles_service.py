import logging

from bot.messaging.events import Events
from bot.services.base_service import BaseService

log = logging.getLogger(__name__)


class AssignableRolesService(BaseService):

    def __init__(self, *, bot):
        super().__init__(bot)

    @BaseService.Listener(Events.on_assignable_role_add)
    async def assignable_role_add(self, role):
        await self.bot.role_route.set_assignable(role.id, True, raise_on_error=True)

    @BaseService.Listener(Events.on_assignable_role_remove)
    async def assignable_role_remove(self, role):
        await self.bot.role_route.set_assignable(role.id, False, raise_on_error=True)

    async def load_service(self):
        pass
