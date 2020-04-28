from pubsub import pub

from bot.events import Events
from bot.services.base_service import BaseService
from bot.data.user_repository import UserRepository

class UserHandling(BaseService):

    def __init__(self):
        pub.subscribe(self.on_user_joined, Events.on_user_joined)

    def on_user_joined(self, user) -> None:
        a = 1
        pass

    async def add_existing_user(self, user: str, guild_id: int) -> None:
        await UserRepository().add_user(user, guild_id)
