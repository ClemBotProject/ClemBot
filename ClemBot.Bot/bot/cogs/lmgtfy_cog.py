import logging
import discord.ext.commands as commands
import bot.extensions as ext
import urllib.parse

log = logging.getLogger(__name__)


class LmgtfyCog(commands.Cog):
    """Implements lmgtfy.app"""

    def __init__(self, bot):
        self.bot = bot

    @ext.command()
    async def lmgfty(self, ctx, *, message):
        await ctx.send(f'https://lmgtfy.app/?q={urllib.parse.urlencode(message)}')


def setup(bot):
    bot.add_cog(LmgtfyCog(bot))
