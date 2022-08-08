# type: ignore
import math
import random
import re

import discord.ext.commands as commands

import bot.extensions as ext
from bot.clem_bot import ClemBot
from bot.utils.logging_utils import get_logger

log = get_logger(__name__)


class OwoCog(commands.Cog):
    def __init__(self, bot: ClemBot):
        self.bot = bot
        self.FACES = ["(・`ω´・)", ";;w;;", "owo", "UwU", ">w<", "^w^"]

    @ext.command()
    @ext.chainable()
    @ext.long_help("Owo's the text given to the command")
    @ext.short_help("owo any string")
    @ext.example("owo hello there")
    async def owo(self, ctx: ext.ClemBotCtx, *, message) -> None:
        await ctx.send(self.owoify(message))

    def owoify(self, text):
        # I have no idea what they are replacing.
        # found this algorithm here: https://honk.moe/tools/owo.html
        # converted from javascript to python
        text = re.sub(r"(?:r|l)", "w", text, len(text))
        text = re.sub(r"(?:R|L)", "W", text, len(text))
        text = re.sub(r"n([aeiou])", r"ny\1", text, len(text))
        text = re.sub(r"N([aeiou])", r"Ny\1", text, len(text))
        text = re.sub(r"N([AEIOU])", r"Ny\1", text, len(text))
        text = re.sub(r"ove", "uv", text, len(text))
        text = re.sub(
            r"\!+",
            " " + self.FACES[math.floor(random.random() * len(self.FACES))] + " ",
            text,
            len(text),
        )

        return text


async def setup(bot: ClemBot) -> None:
    await bot.add_cog(OwoCog(bot))
