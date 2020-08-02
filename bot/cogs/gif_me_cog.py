import logging
import requests

import discord
import discord.ext.commands as commands

from bot.clem_bot import BotSecrets
from bot.consts import Colors

log = logging.getLogger(__name__)


class GifMeCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def gifme(self, ctx, *args):
        
        response = requests.get(
            url="https://api.giphy.com/v1/gifs/random",
            params={
                "api_key": BotSecrets.get_instance().gif_me,
                "rating": "PG-13",
            }
        )
        if(response.status_code == 429):
            embed = discord.Embed(title ="GifMe", color = Colors.Error)
            embed.add_field(name="Too Many Requests", value="The request limit has been reached for the hour.")
        else:
            embed = discord.Embed(title ="GifMe", color = Colors.ClemsonOrange)
            embed.set_image(url=response.json()["data"]["images"]["original"]["url"])
        await ctx.send(embed=embed)    
        await ctx.send("Powered by GIPHY")


def setup(bot):
    bot.add_cog(GifMeCog(bot))
