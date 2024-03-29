import discord

import bot.bot_secrets as bot_secrets
from bot.clem_bot import ClemBot
from bot.consts import Colors
from bot.messaging.events import Events
from bot.services.base_service import BaseService
from bot.utils.logging_utils import get_logger

log = get_logger(__name__)


class BotPingHelpService(BaseService):
    """
    This service responds to messages that only ping/mention ClemBot
    and provides a helpful embed showing the prefix of ClemBot and a link to the site
    """

    def __init__(self, *, bot: ClemBot) -> None:
        super().__init__(bot)

        assert bot.user is not None
        # discord has two ways of mentioning users/accounts for some reason,
        # <@!...> is still used sometimes for some reason?
        self.mention_strs = {f"<@{bot.user.id}>", f"<@!{bot.user.id}>"}

    @BaseService.listener(Events.on_guild_message_received)
    async def on_guild_message_received(self, message: discord.Message) -> None:
        # we only want to respond if the message is ONLY a ping to ClemBot
        if message.content not in self.mention_strs:
            return

        prefix = (await self.bot.get_prefix(message))[2]

        embed = discord.Embed(color=Colors.ClemsonOrange)
        embed.set_author(
            name=self.bot.user.name,
            url=bot_secrets.secrets.site_url,
            icon_url=self.bot.user.display_avatar,
        )
        embed.description = (
            f"My prefix here is `{prefix}` and the help command is `{prefix}help`\n"
            f"If you need more help, visit my website **[clembot.io]({bot_secrets.secrets.site_url})**"
        )

        try:
            msg = await message.channel.send(embed=embed)
        except discord.Forbidden:
            return

        await self.bot.messenger.publish(Events.on_set_deletable, msg=msg, author=message.author)

    async def load_service(self) -> None:
        pass
