from pubsub import pub as pub

from bot.events import Events
from bot.services.base_service import BaseService
from bot.data.guild_repository import GuildRepository

class GuildHandling(BaseService):

    def __init__(self):
        pub.subscribe(self.on_guild_joined, Events.on_guild_joined)

    async def on_guild_joined(self, guild) -> None:
        await GuildRepository().add_guild(guild)

    async def add_guild(self, guild) -> None:
        await GuildRepository().add_guild(guild)
