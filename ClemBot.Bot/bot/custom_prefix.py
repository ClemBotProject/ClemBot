import logging

import discord
from discord.ext import commands

import bot.bot_secrets as bot_secrets
from bot.clem_bot import ClemBot

log = logging.getLogger(__name__)


class CustomPrefix:

    def __init__(self, *, default: str):
        log.info(f'Setting default prefix too: "{default}""')
        self.default = default

    async def get_prefix(self, bot: ClemBot, message: discord.Message):

        prefixes = []

        # Check if bot is in BotOnly mode, if it is we cant get custom prefixes
        # so we have to fall back to self.default
        if not bot_secrets.secrets.bot_only:
            # noinspection PyBroadException
            try:
                # Try to grab the prefixes from the db, raise an error on failure
                # so we know to fallback to the default prefix
                prefixes = await bot.custom_prefix_route.get_custom_prefixes(message.guild.id, raise_on_error=True)
            except Exception:
                pass

        if len(prefixes) == 0:
            prefixes = [self.default]

        return commands.when_mentioned(bot, message) + prefixes
