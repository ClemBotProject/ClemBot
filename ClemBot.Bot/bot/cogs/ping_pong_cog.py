import logging
import math
import random
import time
import discord
import re

import discord.ext.commands as commands

import bot.extensions as ext


class PingPongCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @ext.command(name='ping', aliases=['pong'])
    @ext.long_help('Shows the latency between the bot and Discord')
    @ext.short_help('shows bot latency')
    @ext.example('ping')
    async def ping(self, ctx: commands.Context) -> None:
        embed = discord.Embed(title="ClemBot Latency :stopwatch:")
        embed.add_field(name="WebSocket", value=f"{self.bot.latency * 1000 : 1.2f}ms")
        embed.add_field(name="HTTP", value=":infinity:ms")
        embed.set_footer(text=str(ctx.author), icon_url=ctx.author.display_avatar.url)

        start = time.perf_counter()

        sent = await ctx.send(embed=embed)

        elapsed = (time.perf_counter() - start) * 1000

        embed.remove_field(1)
        embed.add_field(name="HTTP", value=f"{elapsed : 1.2f}ms")

        await sent.edit(embed=embed)

def setup(bot):
    bot.add_cog(PingPongCog(bot))
