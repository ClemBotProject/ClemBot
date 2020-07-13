import logging
import random
import asyncio
import time


import discord
import discord.ext.commands as commands

from bot.consts import Colors

log = logging.getLogger(__name__)


class CoinFlipCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def flip(self, ctx):

        random.seed(time.time())

        embed = discord.Embed(title="Coin Flip", color=Colors.ClemsonOrange)

        heads = discord.File(filename="Heads.jpg",
                             fp="bot/cogs/coin_flip/assets/Heads.jpg")

        tails = discord.File(filename="Tails.jpg",
                             fp="bot/cogs/coin_flip/assets/Tails.jpg")

        if random.randint(0, 1) == 1:
            attachment = heads
            embed.set_thumbnail(url="attachment://Heads.jpg")
        else:
            attachment = tails
            embed.set_thumbnail(url="attachment://Tails.jpg")

        await ctx.send(embed=embed, file=attachment)


def setup(bot):
    bot.add_cog(CoinFlipCog(bot))
