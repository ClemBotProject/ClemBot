import logging
import math
import random
import time
import discord
import re

import discord.ext.commands as commands
from bot.consts import Colors

import bot.extensions as ext


class PingPongCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @ext.command(name='ping', aliases=['pong'])
    @ext.long_help('Shows the latency between the bot\'s internal components and Discord as well as ClemBot\'s API')
    @ext.short_help('shows bot latency')
    @ext.example('ping')
    async def ping(self, ctx: commands.Context) -> None:
        start = time.perf_counter()
        await self.bot.health_check_route.ping()
        clembot_api_latency = time.perf_counter() - start

        embed = discord.Embed(color=Colors.ClemsonOrange, title="ClemBot Latency :stopwatch:")
        embed.add_field(name="Discord WebSocket", value=f"{self.bot.latency * 1000 : 1.2f}ms")
        embed.add_field(name="Discord HTTP", value=":infinity:ms")
        embed.add_field(name="ClemBot API", value=f"{clembot_api_latency * 1000 : 1.2f}ms")
        embed.set_footer(text=str(ctx.author), icon_url=ctx.author.display_avatar.url)

        start = time.perf_counter()

        sent_message = await ctx.send(embed=embed)

        discord_http_latency = (time.perf_counter() - start) * 1000

        embed.remove_field(1)
        embed.insert_field_at(1, name="Discord HTTP", value=f"{discord_http_latency : 1.2f}ms")

        await sent_message.edit(embed=embed)

def setup(bot):
    bot.add_cog(PingPongCog(bot))
