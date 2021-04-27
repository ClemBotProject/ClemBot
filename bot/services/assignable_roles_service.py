import logging

from bot.data.role_repository import RoleRepository
from bot.messaging.events import Events
from bot.services.base_service import BaseService

log = logging.getLogger(__name__)


class AssignableRolesService(BaseService):

    def __init__(self, *, bot):
        super().__init__(bot)

    @BaseService.Listener(Events.on_assignable_role_add)
    async def assignable_role_add(self, role):
        role_repo = RoleRepository()
        await role_repo.set_role_assignable(role.id, True)

    @BaseService.Listener(Events.on_assignable_role_remove)
    async def assignable_role_remove(self, role):
        role_repo = RoleRepository()
        await role_repo.set_role_assignable(role.id, False)

    async def load_service(self):
        pass
