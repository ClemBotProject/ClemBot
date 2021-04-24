import logging
import typing as t

import discord
from discord.ext import commands

log = logging.getLogger(__name__)


class CustomPrefix:

    def __init__(self, *, default: str):
        self.prefixes: t.Dict[int, str] = {}

        log.info(f'Setting default prefix too: "{default}""')
        self.default = default

    def get_prefix(self, bot, message):
        if message.guild.id not in self.prefixes:
            prefixes = self.default
        else:
            prefixes = self.prefixes[message.guild.id]

        return commands.when_mentioned(bot, message) + [prefixes]

    async def set_prefix(self, guild: discord.Guild, prefix: t.Tuple[str]):
        log.info(f'Setting custom prefix in guild: {guild.name}({guild.id}) to "{prefix}""')
        self.prefixes[guild.id] = prefix
