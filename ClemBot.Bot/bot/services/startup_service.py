import asyncio
import logging
import os

from bot.services.base_service import BaseService
import bot.bot_secrets as bot_secrets

log = logging.getLogger(__name__)


class StartupService(BaseService):
    """
    Service to reload discord state into the database on restart
    this is to account for any leaves or joins, new roles, new channels etc
    that happened while the bot was offline
    """

    def __init__(self, *, bot):
        super().__init__(bot)

    async def load_guilds(self):
        tasks = []
        for guild in self.bot.guilds:
            if not await self.bot.guild_route.get_guild(guild.id):
                log.info(f'Loading guild {guild.name}: {guild.id}')
                tasks.append(asyncio.create_task(self.bot.guild_route.add_guild(guild.id, guild.name, guild.owner.id)))
        await asyncio.gather(*tasks)

    async def load_users(self):
        await self.bot.user_route.create_user_bulk(self.bot.users)

    async def load_users_guilds(self):
        for guild in self.bot.guilds:
            await self.bot.guild_route.update_guild_users(guild)

    async def load_roles(self):
        for guild in self.bot.guilds:
            await self.bot.guild_route.update_guild_roles(guild)

        for guild in self.bot.guilds:
            await self.bot.guild_route.update_guild_role_user_mappings(guild)

    async def load_channels(self):
        for guild in self.bot.guilds:
            await self.bot.guild_route.update_guild_channels(guild)

    async def load_threads(self):
        for guild in self.bot.guilds:
            await self.bot.guild_route.update_guild_threads(guild)

    @staticmethod
    def get_full_name(author) -> str:
        return f'{author.name}#{author.discriminator}'

    async def load_service(self):

        # The startup load is too heavy on prod to reset state everytime we restart,
        # So we should only do this on dev bots. We rely on the 24/7 uptime of the bot to
        # Keep the database in sync. Future solutions to this problem
        # Should be heavily researched
        if bool(os.environ.get('PROD')):
            log.warning('Skipping internal state reset on prod deployment')
            self.bot.is_starting_up = False
            return

        if bot_secrets.secrets.bot_only:
            log.warning('Skipping internal state reset in bot_only deployment')
            self.bot.is_starting_up = False
            return

        log.info('Starting development bot startup internal state reset')

        # First load any new guilds so that we can reference them
        log.info('Resetting Guilds')
        await self.load_guilds()

        # Load user guild relationships, takes every guild and sends a complete list of users to the backend
        # to replace the current known state
        log.info('Resetting User_Guilds state')
        await self.load_users_guilds()

        # Reset active roles, send all roles to the backend and delete any not present and add any that are new
        log.info('Resetting Guild Roles state')
        await self.load_roles()

        # Reset active channels, send all channels to the backend and delete any not present and add any that are new
        log.info('Resetting Guild Channels state')
        await self.load_channels()

        # Reset active threads, send all channels to the backend and delete any not present and add any that are new
        log.info('Resetting Guild Threads state')
        await self.load_threads()

        self.bot.is_starting_up = False
