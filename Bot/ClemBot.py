import discord
from discord.ext import commands
from Bot.Cogs.manageClasses import ManageClasses
import logging
log = logging.getLogger(__name__)

class ClemBot(commands.Bot):

    def __init__(self, *args, **kwargs):
        #this super call is to pass the prefix up to the super class
        super().__init__(*args, **kwargs)
        self.load_cogs()

    async def on_ready(self):
        log.info(f'Logged on as {self.user}')

    async def on_message(self, message):
        log.info(f'Message from {message.author}: {message.content}')
        await self.process_commands(message)

    def load_cogs(self):
        log.info('Loading cogs')
        self.load_extension("Bot.Cogs.manageClasses")

