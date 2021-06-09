import logging

import discord
import discord.ext.commands as commands

import bot.extensions as ext
from bot.consts import Colors
from bot.messaging.events import Events
from bot.utils import converters

log = logging.getLogger(__name__)

'''
class RemindCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @ext.command()
    @ext.long_help(
        """
        This command will direct message the user with their message at specified time in the future.

        This command supports many different time specifiers as listed below.
        Specifiers:
            - years: `Y`, `y`, `year`, `years`
            - months: `M`, `month`, `months`
            - weeks: `w`, `W`, `week`, `weeks`
            - days: `d`, `D`, `day`, `days`
            - hours: `H`, `h`, `hour`, `hours`
            - minutes: `m`, `min`, `minute`, `minutes`
            - seconds: `S`, `sec`, `s`, `second`, `seconds`

        """
    )
    @ext.short_help('Creates a reminder')
    @ext.example((
        'remind 24h',
        'remind 5m Exam!',
        'remind 1h Homework!',
        'remind 4y Graduation',
        'remind 3y1M4w1d5h9m2s Pi'
    ))
    async def remind(self, ctx: commands.Context, wait: converters.Duration):

        try:
            embed = discord.Embed(title="⏰Reminder", color = Colors.ClemsonOrange)
            await self.bot.messenger.publish(
               Events.on_set_reminder,
               ctx.author.id,
               wait,
               ctx.message.id,
               ctx.message.jump_url)
            embed.add_field(name="Status", value = "Reminder Created") 
        except Exception:

            embed = discord.Embed(title="⏰Reminder", color = Colors.Error)
            embed.add_field(name="Status", value = "Error")
        await ctx.send(embed=embed)
            

def setup(bot):
    bot.add_cog(RemindCog(bot))
'''