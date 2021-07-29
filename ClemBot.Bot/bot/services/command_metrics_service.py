import asyncio
import logging
import typing as t

import discord
from discord.ext import commands

from bot.consts import Claims
from bot.messaging.events import Events
from bot.services.base_service import BaseService

log = logging.getLogger(__name__)


class CommandMetricsService(BaseService):

    def __init__(self, *, bot):
        super().__init__(bot)

    @BaseService.Listener(Events.on_after_command_invoke)
    async def log_invoked_commands(self, ctx: commands.Context):

        await self.bot.commands_route.add_command_invocation(ctx.command.name,
                                                             ctx.guild.id,
                                                             ctx.channel.id,
                                                             ctx.author.id)

    async def load_service(self):
        pass
