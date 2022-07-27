from bot.messaging.events import Events
from bot.services.base_service import BaseService
from bot.utils.logging_utils import get_logger

log = get_logger(__name__)


class WelcomeMessageService(BaseService):
    def __init__(self, *, bot):
        super().__init__(bot)

    @BaseService.listener(Events.on_user_joined)
    async def user_joined(self, user):
        message = await self.bot.welcome_message_route.get_welcome_message(user.guild.id)

        if message and not user.bot:
            await user.send(message)

    async def load_service(self):
        pass
