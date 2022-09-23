import bot.bot_secrets as bot_secrets
import bot.extensions as ext
from bot.clem_bot import ClemBot
from bot.consts import Claims
from bot.errors import ClaimsAccessError
from bot.messaging.events import Events
from bot.services.base_service import BaseService


class ClaimsService(BaseService):
    def __init__(self, *, bot: ClemBot):
        super().__init__(bot)

    @BaseService.listener(Events.on_claims_check)
    async def on_claims_check(self, ctx: ext.ClemBotCtx) -> None:
        assert ctx.command is not None
        if not isinstance(ctx.command, ext.ExtBase):
            # If the command isn't an extension command let it through, we don't need to think about it
            return

        if ctx.command.ignore_claims_pre_invoke:
            # The command is going to check the claims in the command body, nothing else to do
            return

        if await self.bot.claims_check(ctx):
            return

        # User does not have correct claims - raise error to stop execution
        claims_str = "\n".join(ctx.command.claims)
        raise ClaimsAccessError(
            f"Missing claims to run this operation, Need any of the following\n ```\n{claims_str}```"
            f"\n **Help:** For more information on how claims work please visit my website [Link!]"
            f"({bot_secrets.secrets.docs_url}/claims)\n"
            f"or run the `{ctx.prefix}help claims` command"
        )

    async def load_service(self) -> None:
        pass
