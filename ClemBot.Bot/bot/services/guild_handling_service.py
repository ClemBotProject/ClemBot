import discord

import bot.utils.log_serializers as serializers
from bot.clem_bot import ClemBot
from bot.consts import Colors, OwnerDesignatedChannels
from bot.messaging.events import Events
from bot.services.base_service import BaseService
from bot.utils.logging_utils import get_logger

log = get_logger(__name__)


class GuildHandlingService(BaseService):
    def __init__(self, *, bot: ClemBot):
        super().__init__(bot)

    @BaseService.listener(Events.on_guild_joined)
    async def on_guild_joined(self, guild: discord.Guild) -> None:
        log.info(f"Loading guild {guild.name}: {guild.id}")

        await self._send_guild_joined_embed(guild)

        assert guild.owner is not None

        await self.bot.guild_route.add_guild(
            guild.id, guild.name, guild.owner.id, raise_on_error=True
        )
        log.info(f"Finished Loading guild {guild.name}: {guild.id}")

        await self.bot.guild_route.update_guild_users(guild)
        log.info(f"Finished Loading guild users {guild.name}: {guild.id}")

        await self.bot.guild_route.update_guild_roles(guild)
        log.info(f"Finished Loading guild roles {guild.name}: {guild.id}")

        await self.bot.guild_route.update_guild_role_user_mappings(guild)
        log.info(f"Finished Loading guild role_user mappings {guild.name}: {guild.id}")

        # The guild has been initialized, broadcast this to the rest
        # of the services
        await self.bot.messenger.publish(Events.on_new_guild_initialized, guild)

        log.info("Guild {guild_name}: {guild_id} loaded", guild_name=guild.name, guild_id=guild.id)

        await self.bot.messenger.publish(
            Events.on_broadcast_designated_channel,
            OwnerDesignatedChannels.server_join_log,
            f"{guild.name}: {guild.id} initialization successful",
        )

    @BaseService.listener(Events.on_guild_update)
    async def on_guild_edit(self, before: discord.Guild, after: discord.Guild) -> None:
        assert before.owner is not None
        assert after.owner is not None

        if before.name != after.name or before.owner.id != after.owner.id:
            await self.bot.guild_route.edit_guild(after.id, after.name, after.owner.id)

    @BaseService.listener(Events.on_guild_leave)
    async def on_guild_leave(self, guild: discord.Guild) -> None:
        log.info("Bot removed from {guild}", guild=serializers.log_guild(guild))

        await self.bot.messenger.publish(
            Events.on_broadcast_designated_channel,
            OwnerDesignatedChannels.server_join_log,
            f"Bot removed from {guild.name}: {guild.id}",
        )

        await self.bot.guild_route.leave_guild(guild.id, raise_on_error=True)

    async def _send_guild_joined_embed(self, guild: discord.Guild) -> None:

        # We arent sure what values will be there, some guilds have an odd guild object
        # Do a blanket try catch to make sure that sending the embed doesnt cause the
        # Join routines to not run if the embed throws
        try:
            assert guild.owner is not None

            guild_str = f"{self.bot.user.name} added to a new guild\n\n"

            guild_str += f"Id: {guild.id}\n"
            guild_str += f"Name: {guild.name}\n"
            guild_str += f"Owner: {guild.owner.name}#{guild.owner.discriminator}\n"
            guild_str += f"Created At: {guild.created_at}\n"
            guild_str += f"User Count: {len([m for m in guild.members if not m.bot])}\n"
            guild_str += f"Bot Count: {len([m for m in guild.members if m.bot])}\n"
            if guild.icon:
                guild_str += f"Server avatar: {guild.icon.url}\n"

            await self.bot.messenger.publish(
                Events.on_broadcast_designated_channel,
                OwnerDesignatedChannels.server_join_log,
                guild_str,
            )
        except Exception as e:
            log.error(f"Sending new guild embed failed for guild: {guild.id} with error {e}")
            await self.bot.messenger.publish(
                Events.on_broadcast_designated_channel,
                OwnerDesignatedChannels.server_join_log,
                f"New guild joined embed failed Guild Id: {guild.id}",
            )

    async def load_service(self) -> None:
        pass
