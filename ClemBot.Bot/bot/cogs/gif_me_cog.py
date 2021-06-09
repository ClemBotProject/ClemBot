import json
import logging

import aiohttp
import discord
import discord.ext.commands as commands

import bot.bot_secrets as bot_secrets
import bot.extensions as ext
from bot.consts import Colors
from bot.messaging.events import Events

log = logging.getLogger(__name__)


class GifMeCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @ext.command(aliases=['gif'])
    @ext.long_help(
        'Gets a random gif from giphy'
    )
    @ext.short_help('shows a random gif')
    @ext.example('gifme')
    async def gifme(self, ctx, *args):

        params = {
            "api_key": bot_secrets.secrets.gif_me_token,
            "rating": "PG-13"
        }

        async with aiohttp.ClientSession() as session:
            async with await session.get(url="https://api.giphy.com/v1/gifs/random", params=params)as resp:
                response = json.loads(await resp.text())

        response_info = response["meta"]
        if (response_info["status"] != 200):
            embed = discord.Embed(title="GifMe", color=Colors.Error)
            embed.add_field(name="Error", value=f"{response_info['status']}: {response_info['msg']}")
        else:
            embed = discord.Embed(title="GifMe", color=Colors.ClemsonOrange)
            embed.set_image(url=response["data"]["images"]["original"]["url"])
            embed.set_footer(text="Powered by GIPHY")
        msg = await ctx.send(embed=embed)
        await self.bot.messenger.publish(Events.on_set_deletable,
                                         msg=msg,
                                         author=ctx.author,
                                         timeout=60)


def setup(bot):
    bot.add_cog(GifMeCog(bot))
