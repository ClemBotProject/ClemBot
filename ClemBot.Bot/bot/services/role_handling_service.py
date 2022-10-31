import discord

import bot.utils.log_serializers as serializers
from bot.clem_bot import ClemBot
from bot.messaging.events import Events
from bot.services.base_service import BaseService
from bot.utils.log_serializers import log_role, log_user
from bot.utils.logging_utils import get_logger

log = get_logger(__name__)


class RoleHandlingService(BaseService):
    def __init__(self, *, bot: ClemBot) -> None:
        super().__init__(bot)

    @BaseService.listener(Events.on_guild_role_create)
    async def on_role_create(self, role: discord.Role) -> None:
        await self.bot.role_route.create_role(
            role.id, role.name, role.permissions.administrator, role.guild.id, raise_on_error=True
        )

    @BaseService.listener(Events.on_guild_role_delete)
    async def on_role_delete(self, role: discord.Role) -> None:
        log.info(
            "Role: {role} deleted in guild: {guild}",
            role=serializers.log_role(role),
            guild=serializers.log_guild(role.guild),
        )

        await self.bot.role_route.remove_role(role.id, raise_on_error=True)

    @BaseService.listener(Events.on_guild_role_update)
    async def on_role_update(self, before: discord.Role, after: discord.Role) -> None:
        # Only send role updates that changed values we care about to the database
        if (
            before.name == after.name
            and before.permissions.administrator == after.permissions.administrator
        ):
            return

        log.info(
            "Role:{before} {after} updated in guild: {guild}",
            before=serializers.log_role(before),
            after=serializers.log_role(after),
            guild=serializers.log_guild(after.guild),
        )

        await self.bot.role_route.edit_role(
            after.id, after.name, after.permissions.administrator, raise_on_error=True
        )

    @BaseService.listener(Events.on_user_join_initialized)
    async def add_auto_assigned_roles(self, member: discord.Member) -> None:
        roles = await self.bot.role_route.get_guilds_auto_assigned_roles(member.guild.id)

        d_roles: list[discord.Role] = []
        for r in roles:
            d_role = member.guild.get_role(r.id)

            if not d_role:
                log.warning(
                    "Invalid role id returned from database in auto assign handler Role: {role}",
                    role=r.id,
                )
                continue

            d_roles.append(d_role)

        log.info(
            "Auto adding roles: {roles} to member: {member}",
            roles=[log_role(r) for r in d_roles],
            member=log_user(member),
        )
        await member.add_roles(*d_roles, reason="Adding auto join roles to user")

    async def load_service(self) -> None:
        pass
