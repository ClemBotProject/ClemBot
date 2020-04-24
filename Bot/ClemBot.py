import discord
from discord.ext import commands
from Bot.Cogs.manageClasses import ManageClasses
from logger import botlog as log

class ClemBot(commands.Bot):

    def __init__(self, *args, **kwargs):
        #this super call is to pass the prefix up to the super class
        super().__init__(*args, **kwargs)
        self.load_cogs()

    async def on_ready(self):
        log.info(f'Logged on as {self.user}')

    async def on_message(self, message):
        log.info('Message from {0.author}: {0.content}'.format(message))
        await self.process_commands(message)

    def load_cogs(self):
        log.info('Loading cogs')
        self.load_extension("Bot.Cogs.manageClasses")

