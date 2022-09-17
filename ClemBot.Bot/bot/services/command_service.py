import bot.extensions as ext
import bot.utils.log_serializers as serializers
from bot.clem_bot import ClemBot
from bot.consts import Claims
from bot.errors import CommandRestrictionError, SilentCommandRestrictionError
from bot.messaging.events import Events
from bot.services.base_service import BaseService
from bot.utils.logging_utils import get_logger

log = get_logger(__name__)


class CommandService(BaseService):
    def __init__(self, *, bot: ClemBot):
        super().__init__(bot)

    @BaseService.listener(Events.on_after_command_invoke)
    async def log_invoked_commands(self, ctx: ext.ClemBotCtx) -> None:
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

    @BaseService.listener(Events.on_restrictions_check)
    async def on_restrictions_check(self, ctx: ext.ClemBotCtx) -> None:
        assert ctx.command is not None
        if not ctx.command.allow_disable:
            return

        if await self.bot.claim_route.check_claim_user(Claims.bypass_disabled_commands, ctx.author):
            return

        assert ctx.guild is not None
        assert ctx.channel is not None

        guild_id = ctx.guild.id
        channel_id = ctx.channel.id
        command_name = ctx.command.name

        disabled, silently_fail = await self.bot.commands_route.get_status(
            guild_id, channel_id, command_name
        )

        if not disabled:
            return

        if not silently_fail:
            raise CommandRestrictionError(
                f"The command `{command_name}` has been disabled.\n"
                f"Type `{ctx.prefix}cmd {command_name}` to see where it's been disabled."
            )

        raise SilentCommandRestrictionError()

    async def load_service(self) -> None:
        pass
