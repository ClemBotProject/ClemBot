import logging
import seqlog

import discord
from bot.consts import Colors

from bot.messaging.events import Events
from bot.services.base_service import BaseService
import bot.bot_secrets as bot_secrets

log: seqlog.StructuredLogger = logging.getLogger(__name__)  # type: ignore


class BotPingHelpService(BaseService):
    """
    This service responds to messages that only ping/mention ClemBot
    and provides a helpful embed showing the prefix of ClemBot and a link to the site
    """

    def __init__(self, *, bot):
        super().__init__(bot)
        
        # discord has two ways of mentioning users/accounts for some reason,
        # <@!...> is still used sometimes for some reason?
        self.mention_strs = {f"<@{bot.user.id}>", f"<@!{bot.user.id}>"}

    @BaseService.Listener(Events.on_guild_message_received)
    async def on_guild_message_received(self, message: discord.Message) -> None:
        # we only want to respond if the message is ONLY a ping to ClemBot
        if message.content not in self.mention_strs:
            return
        
        prefix = await self.bot.current_prefix(message)

        embed = discord.Embed(color=Colors.ClemsonOrange)
        embed.set_author(name=self.bot.user.name, url=bot_secrets.secrets.site_url, icon_url=self.bot.user.avatar.url)
        embed.description = f"My prefix here is `{prefix}` and the help command is `{prefix}help`\n" \
            f"If you need more help, visit my website **[clembot.io]({bot_secrets.secrets.site_url})**"

        try:
            msg = await message.channel.send(embed=embed)
        except discord.Forbidden:
            return

        await self.bot.messenger.publish(Events.on_set_deletable, msg=msg, author=message.author)
        
    async def load_service(self):
        pass
