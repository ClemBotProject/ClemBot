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

    @commands.command(aliases= ['gif'])
    async def gifme(self, ctx, *args):
        
        response = requests.get(
            url="https://api.giphy.com/v1/gifs/random",
            params={
                "api_key": BotSecrets.get_instance().gif_me_token,
                "rating": "PG-13",
            }
        )
        response_info = response.json()["meta"]
        if(response_info["status"] != 200):
            embed = discord.Embed(title ="GifMe", color = Colors.Error)
            embed.add_field(name="Error", value=f"{response_info['status']}: {response_info['msg']}")
        else:
            embed = discord.Embed(title ="GifMe", color = Colors.ClemsonOrange)
            embed.set_image(url=response.json()["data"]["images"]["original"]["url"])
            embed.set_footer(text = "Powered by GIPHY")
        await ctx.send(embed=embed)    


def setup(bot):
    bot.add_cog(GifMeCog(bot))
