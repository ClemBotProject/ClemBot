import logging

import discord
from discord.ext import commands

import bot.bot_secrets as bot_secrets
from bot.clem_bot import ClemBot
from bot.errors import TagPrefixRequestError

log = logging.getLogger(__name__)


class CustomTagPrefix:

    def __init__(self, *, default: str):
        log.info(f'Setting default tag prefix too: "{default}""')
        self.default = default

    async def get_tag_prefix(self, bot: ClemBot, message: discord.Message):

        tagprefixes = []

        # Check if bot is in BotOnly mode, if it is we cant get custom tag prefixes
        # so we have to fall back to self.default
        if not bot_secrets.secrets.bot_only:
            # noinspection PyBroadException
            try:
                # Try to grab the prefixes from the db, raise an error on failure
                # and bailout, we cant respond to anything at the moment
                tagprefixes = await bot.custom_tag_prefix_route.get_custom_tag_prefixes(message.guild.id, raise_on_error=True)
            except Exception as e:
                log.error('Custom tagprefix request failed with error: {error}', error=e)
                raise TagPrefixRequestError('Requesting custom tagprefix from the api failed')

        if len(tagprefixes) == 0:
            tagprefixes = [self.default]

        return commands.when_mentioned(bot, message) + tagprefixes
