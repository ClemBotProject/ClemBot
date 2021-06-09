import logging

from bot.messaging.events import Events
from bot.services.base_service import BaseService

log = logging.getLogger(__name__)


class WelcomeMessageService(BaseService):

    def __init__(self, *, bot):
        super().__init__(bot)

    @BaseService.Listener(Events.on_user_joined)
    async def user_joined(self, user):
        message = await self.bot.welcome_message_route.get_welcome_message(user.guild.id)

        if message and not user.bot:
            await user.send(message)

    async def load_service(self):
        pass
