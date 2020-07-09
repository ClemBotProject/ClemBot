import logging

from bot.data.role_repository import RoleRepository
from bot.messaging.events import Events
from bot.services.base_service import BaseService

log = logging.getLogger(__name__)

class RoleHandlingService(BaseService):

    def __init__(self, *, bot):
        super().__init__(bot)

    @BaseService.Listener(Events.on_guild_role_create)
    async def on_role_create(self, role):
        await RoleRepository().add_or_update_role(role, role.guild.id)

    @BaseService.Listener(Events.on_guild_role_delete)
    async def on_role_delete(self, role):
        await RoleRepository().delete_role(role.id)
        await self.refresh_roles(role)

    @BaseService.Listener(Events.on_guild_role_update)
    async def on_role_update(self, before, after):
        await self.refresh_roles(after)

    async def refresh_roles(self, role):
        guild = role.guild
        for role in guild.roles:
            await RoleRepository().add_or_update_role(role, guild.id)

    async def load_service(self):
        role_repo = RoleRepository()
        for guild in self.bot.guilds:
            log.info(f'Loading Roles from {guild.name}')
            db_roles = [i[0] for i in await role_repo.get_role_ids(guild.id)]
            api_roles = [r.id for r in guild.roles]

            for deleted_role_id in set(db_roles) - set(api_roles):
                log.info(f'Missing role {deleted_role_id} found, removing from local db')
                await role_repo.delete_role(deleted_role_id)

            for role in guild.roles:
                log.info(f'Loading role "{role.name}" in {guild.name}')
                await role_repo.add_or_update_role(role, guild.id)
