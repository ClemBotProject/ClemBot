import asyncio
import logging
import random
import typing as t

import discord
import discord.ext.commands as commands

import bot.extensions as ext
from bot.consts import Colors


class Symbols:
    combined = '🍎🍐🍇🍊🍋🍓🍒💎'

    apple = '🍎'
    pear = '🍐'
    grape = '🍇'
    orange = '🍊'
    lemon = '🍋'
    cherry = '🍒'
    strawberry = '🍓'
    jackpot = '💎'


PAY_TABLE = {
    Symbols.apple: 1,
    Symbols.pear: 2,
    Symbols.grape: 5,
    Symbols.orange: 10,
    Symbols.lemon: 20,
    Symbols.cherry: 50,
    Symbols.strawberry: 100,
    Symbols.jackpot: 500
}

MULTIPLIERS = {
    1: 1,
    2: 2,
    3: 5,
    4: 20,
    5: 50
}

WEIGHTS = [
    100,
    75,
    65,
    50,
    25,
    10,
    5,
    2
]

PHRASES = [
    'Will you get lucky?',
    "You're feeling lucky I see",
    "You're on a roll",
    'Keep going hotshot',
    'Good fortune in your future',
    "Dang you're good",
    'Ohh come on, one more try!',
    'Absolutely Stupendous!',
    'This is the start of something great',
    'Right on!',
    'High score incoming!'
]

log = logging.getLogger(__name__)
SLOTS_COMMAND_COOLDOWN = 30


class OgSlotsCog(commands.Cog):

    def __init__(self, bot) -> None:
        self.bot = bot

    @ext.command()
    @commands.cooldown(1, SLOTS_COMMAND_COOLDOWN, commands.BucketType.user)
    @ext.long_help(
        'A slot machine inside discord with a chance to win fame and fortune'
    )
    @ext.short_help('How lucky are you?')
    @ext.example('slots')
    async def ogslots(self, ctx):
        results = random.choices(Symbols.combined, weights=WEIGHTS, k=5)
        score = self.calculate_score(results)

        output = list('⬜' * len(results))

        quote = random.choice(PHRASES)

        slotstitle = '💎 ClemBot Slot Machine 💎'

        def slots_rolling(input, spinstatus):
            slotembed = discord.Embed(title=f'{slotstitle}',
                                      color=Colors.ClemsonOrange,
                                      description=quote)

            slotembed.set_footer(text=f'{self.get_full_name(ctx.author)}', icon_url=ctx.author.display_avatar.url)
            slotembed.add_field(name=input, value=spinstatus, inline=False)
            return slotembed

        msg = await ctx.send(embed=slots_rolling(' | '.join(output), 'Spinning!!'))

        for i in range(len(results)):
            output[i] = results[i]
            await msg.edit(embed=slots_rolling(' | '.join(output), 'Spinning!!'))
            await asyncio.sleep(1)

        final = slots_rolling(' | '.join(output), 'Spin Complete')
        final.add_field(name='SCORE!!', value=score)

        await msg.edit(embed=final)

    def calculate_score(self, results: t.List[str]) -> int:
        groups = []
        curr_group = []

        for i, val in enumerate(results):
            if val in curr_group or len(curr_group) == 0:
                curr_group.append(val)
            elif i == len(results):
                groups.append(val)
            else:
                groups.append(curr_group)
                curr_group = [val]

        groups.append(curr_group)

        total_score = 0
        for g in groups:
            total_score += PAY_TABLE[g[0]] * len(g) * MULTIPLIERS[len(g)]

        return total_score

    def get_full_name(self, author) -> str:
        return f'{author.name}#{author.discriminator}'


def setup(bot):
    bot.add_cog(OgSlotsCog(bot))