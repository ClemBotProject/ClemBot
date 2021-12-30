import logging

import discord

from bot.messaging.events import Events
from bot.services.base_service import BaseService

log = logging.getLogger(__name__)


class RoleHandlingService(BaseService):

    def __init__(self, *, bot):
        super().__init__(bot)

    @BaseService.Listener(Events.on_guild_role_create)
    async def on_role_create(self, role):
        await self.bot.role_route.create_role(role.id,
                                              role.name,
                                              role.permissions.administrator,
                                              role.guild.id,
                                              raise_on_error=True)

    @BaseService.Listener(Events.on_guild_role_delete)
    async def on_role_delete(self, role):
        log.info('Role: {role_id} deleted in guild: {role_guild}', role_id=role.id, role_guild=role.guild.id)
        await self.bot.role_route.remove_role(role.id, raise_on_error=True)

    @BaseService.Listener(Events.on_guild_role_update)
    async def on_role_update(self, before, after: discord.Role):
        log.info('Role: {after} updated in guild: {role_guild}', after=after.id, role_guild=after.guild.id)
        await self.bot.role_route.edit_role(after.id, after.name, after.permissions.administrator, raise_on_error=True)

    async def load_service(self):
        pass
