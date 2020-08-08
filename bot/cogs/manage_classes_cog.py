import logging

import discord
import discord.ext.commands as commands

log = logging.getLogger(__name__)


class ManageClassesCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self._last_member = None


def setup(bot): 
    bot.add_cog(ManageClassesCog(bot))
