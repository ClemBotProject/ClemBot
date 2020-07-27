import logging

import discord

from bot.data.user_repository import UserRepository
from bot.messaging.events import Events
from bot.services.base_service import BaseService

log = logging.getLogger(__name__)

class UserHandlingService(BaseService):

    def __init__(self, *, bot):
        super().__init__(bot)

    @BaseService.Listener(Events.on_user_joined)
    async def on_user_joined(self, user) -> None:
        log.info(f'{user.name} has joined!')
        await self.add_user(user, user.guild.id)

    @BaseService.Listener(Events.on_new_guild_initialized)
    async def on_new_guild_init(self, guild):
        await self.load_users(guild)

    async def add_user(self, user, guild_id: int) -> None:
        await UserRepository().add_user(user, guild_id)

    async def load_users(self, guild: discord.Guild):
        for user in guild.members:
            user_string = f'{self.get_full_name(user)}:{user.id}'
            guild_string = f'{guild.name}:{guild.id}'
            log.info(f'Loading user: {user_string} in Guild: {guild_string}')
            await self.add_user(user, guild.id)

    def get_full_name(self, author) -> str: 
        return f'{author.name}#{author.discriminator}' 

    async def load_service(self) -> None:
        for guild in self.bot.guilds:
            log.info(f'Initializing members of {guild.name}')
            await self.load_users(guild)
