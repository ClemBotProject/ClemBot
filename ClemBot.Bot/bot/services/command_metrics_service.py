from discord.ext import commands
from bot.clem_bot import ClemBot

import bot.utils.log_serializers as serializers
from bot.messaging.events import Events
from bot.services.base_service import BaseService
from bot.utils.logging_utils import get_logger
import bot.extensions as ext

log = get_logger(__name__)


class CommandMetricsService(BaseService):
    def __init__(self, *, bot: ClemBot):
        super().__init__(bot)

    @BaseService.listener(Events.on_after_command_invoke)
    async def log_invoked_commands(self, ctx: ext.ClemBotContext[ClemBot]) -> None:
        assert ctx.command is not None
        assert ctx.guild is not None

        log.info(
            'Command "{command}" invoked in guild:{guild} by user:{user}',
            command=ctx.command.name,
            guild=serializers.log_guild(ctx.guild),
            user=serializers.log_user(ctx.author),
        )

        await self.bot.commands_route.add_command_invocation(
            ctx.command.qualified_name, ctx.guild.id, ctx.channel.id, ctx.author.id
        )

    async def load_service(self) -> None:
        pass
