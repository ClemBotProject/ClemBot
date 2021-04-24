import logging

from bot.data.welcome_message_repository import WelcomeMessageRepository
from bot.messaging.events import Events
from bot.services.base_service import BaseService

log = logging.getLogger(__name__)


class WelcomeMessageService(BaseService):

    def __init__(self, *, bot):
        super().__init__(bot)

    @BaseService.Listener(Events.on_user_joined)
    async def assignable_role_add(self, user):
        repo = WelcomeMessageRepository()

        message = await repo.get_welcome_message(user.guild.id)

        if message and not user.bot:
            await user.send(message)

    async def load_service(self):
        pass
