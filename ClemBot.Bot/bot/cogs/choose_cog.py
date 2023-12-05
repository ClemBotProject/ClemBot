import re
from random import choice

import discord
import discord.ext.commands as commands

import bot.extensions as ext
from bot.clem_bot import ClemBot
from bot.consts import Colors
from bot.utils.logging_utils import get_logger

log = get_logger(__name__)


class ChooseCog(commands.Cog):
    def __init__(self, bot: ClemBot) -> None:
        self.bot = bot

    @ext.command()
    @ext.long_help("Given a comma separated list, this command will choose between them randomly")
    @ext.short_help("Chooses an item from the given list randomly")
    @ext.example(
        (
            "choose a,b,c,d,e",
            "choose a, b, c, d, e",
        )
    )
    async def choose(self, ctx: ext.ClemBotCtx, *, choices_list: str) -> None:
        error_title = ""
        error_message = ""

        # split string on comma to get separate options
        options = choices_list.split(",")

        # remove leading/trailing spaces to ensure no whitespace from original formatting
        options = [x.lstrip() for x in options]

        # check that there are at least 2 arguments
        if len(options) < 2:
            error_title = "Invalid argument(s)"
            error_message = f"Are you sure you used the correct format? See `{await self.bot.current_prefix(ctx)}help choose` for info."

        # if there are any errors send the error message and end the function
        if error_title != "":
            embed = discord.Embed(title="Choose", color=Colors.Error)
            embed.add_field(name="ERROR: " + error_title, value=error_message, inline=False)
            await ctx.send(embed=embed)
            return

        # otherwise choose one of the values and return it in a message
        chosen_value = choice(options)
        embed = discord.Embed(
            title="Choice",
            color=Colors.ClemsonOrange,
        )
        embed.add_field(
            name="Given Options",
            value=choices_list,
            inline=False,
        )
        embed.add_field(
            name="Chosen Option",
            value=chosen_value,
            inline=False,
        )
        await ctx.send(embed=embed)


async def setup(bot: ClemBot) -> None:
    await bot.add_cog(ChooseCog(bot))
