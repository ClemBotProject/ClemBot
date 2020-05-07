
from bot.events import Events
from bot.services.base_service import BaseService
from bot.data.guild_repository import GuildRepository

class GuildHandling(BaseService):

    def __init__(self):
        pass

    async def on_guild_joined(self, guild) -> None:
        await GuildRepository().add_guild(guild)

    async def add_guild(self, guild) -> None:
        await GuildRepository().add_guild(guild)
