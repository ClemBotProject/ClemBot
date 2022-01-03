import asyncio
import dataclasses
import logging
import random
import typing as t

import discord
import discord.ext.commands as commands
import numpy as np

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


@dataclasses.dataclass
class PayLine:
    multiplier: int
    weights: t.Dict[str, float]


VERTICAL_MULTIPLIERS = {
    1: 1,
    2: 2,
    3: 10,
}

DIAGONAL_MULTIPLIERS = {
    1: 1,
    2: 1,
    3: 2
}

HORIZONTAL_MULTIPLIERS = {
    1: 1,
    2: 2,
    3: 5,
    4: 20,
    5: 50
}

NUM_COLUMNS = 5
NUM_ROWS = 3

PAYLINE_VALUES = [
    PayLine(multiplier=1, weights={
        Symbols.apple: 125,
        Symbols.pear: 85,
        Symbols.grape: 75,
        Symbols.orange: 50,
        Symbols.lemon: 25,
        Symbols.cherry: 10,
        Symbols.strawberry: 5,
        Symbols.jackpot: 2
    }),
    PayLine(multiplier=4, weights={
        Symbols.apple: 150,
        Symbols.pear: 100,
        Symbols.grape: 80,
        Symbols.orange: 65,
        Symbols.lemon: 27,
        Symbols.cherry: 10,
        Symbols.strawberry: 5,
        Symbols.jackpot: 2
    }),
    PayLine(multiplier=2, weights={
        Symbols.apple: 135,
        Symbols.pear: 90,
        Symbols.grape: 75,
        Symbols.orange: 50,
        Symbols.lemon: 20,
        Symbols.cherry: 10,
        Symbols.strawberry: 5,
        Symbols.jackpot: 2
    })
]

COLUMN_MULTIPLIERS = [
    1,
    2,
    3,
    2,
    1
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
    'High score incoming!',
    'You got this!'
]

log = logging.getLogger(__name__)
SLOTS_COMMAND_COOLDOWN = 60


class SlotsCog(commands.Cog):

    def __init__(self, bot) -> None:
        self.bot = bot

    @ext.command(aliases=['slotmachine', '🎰'])
    # @commands.cooldown(1, SLOTS_COMMAND_COOLDOWN, commands.BucketType.user)
    @ext.long_help(
        'A slot machine inside discord with a chance to win fame and fortune'
    )
    @ext.short_help('How lucky are you?')
    @ext.example('slots')
    async def slots(self, ctx):
        paylines = self._generate_paylines()

        score = self._calculate_score(np.array(paylines))

        return await ctx.send(score)

        """
        results = [random.choices(Symbols.combined, weights=WEIGHTS, k=5) for _ in range(3)]
        # await ctx.send(results)
        # score = self.calculate_score(results)
        # await ctx.send(score)

        output = [list('⬜' * len(results[0])) for _ in range(3)]

        quote = random.choice(PHRASES)

        slotstitle = '💎 ClemBot Slot Machine 💎'

        def slots_rolling(input, spinstatus):
            slotembed = discord.Embed(title=f'{slotstitle}',
                                      color=Colors.ClemsonOrange,
                                      description=quote)

            slotembed.set_footer(text=f'{self.get_full_name(ctx.author)}', icon_url=ctx.author.display_avatar.url)
            slotembed.add_field(name=input, value=spinstatus, inline=False)
            return slotembed

        val = '\n'.join(' | '.join(row) for row in output)
        msg = await ctx.send(embed=slots_rolling(' | '.join(val), 'Spinning!!'))

        for i in range(len(results[0])):
            for j in range(len(results)):
                output[j][i] = results[j][i]

            val = '\n'.join(' | '.join(row) for row in output)
            await msg.edit(embed=slots_rolling(val, 'Spinning!!'))
            await asyncio.sleep(1)

        final = slots_rolling(' | '.join(output), 'Spin Complete')
        final.add_field(name='SCORE!!', value=score)

        await msg.edit(embed=final)
        """

    def _calculate_score(self, paylines: np.ndarray) -> int:

        # Calculate the horizontal scores, while counting groupings of one
        horizontal_score = 0
        for i, line in enumerate(paylines):
            horizontal_score += self._calculate_line_score(results=line,
                                                           consecutive_multipliers=HORIZONTAL_MULTIPLIERS,
                                                           count_singles=True,
                                                           payline_multiplier=PAYLINE_VALUES[i].multiplier)

        # Transpose the matrix to easily check for vertical groupings
        flipped_arr = np.rot90(paylines)
        vertical_score = 0
        for i, line in enumerate(flipped_arr):
            vertical_score += self._calculate_line_score(results=line,
                                                         consecutive_multipliers=VERTICAL_MULTIPLIERS,
                                                         count_singles=False,
                                                         payline_multiplier=COLUMN_MULTIPLIERS[i])

        # Grab diagonals with a length greater than one and check for more groupings
        diagonals = self._get_all_diagonals(paylines)
        diagonals = [d for d in diagonals if len(d) > 1]

        diagonal_score = 0
        for i, line in enumerate(diagonals):
            diagonal_score += self._calculate_line_score(results=line,
                                                         count_singles=False,
                                                         consecutive_multipliers=DIAGONAL_MULTIPLIERS)

        return horizontal_score + vertical_score + diagonal_score

    def _calculate_line_score(self, *,
                              results: t.List[str],
                              count_singles: bool,
                              consecutive_multipliers: t.Dict[int, int],
                              payline_multiplier: int = 1) -> int:

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

        # Filter out the single groups if we aren't supposed to count those
        if not count_singles:
            groups = [g for g in groups if len(g) > 1]

        total_score = 0
        for i, g in enumerate(groups):
            total_score += PAY_TABLE[g[0]] * len(g) * consecutive_multipliers[len(g)] * payline_multiplier

        return total_score

    def _get_all_diagonals(self, matrix: np.ndarray):
        """https://stackoverflow.com/a/6313414"""
        diags = [matrix[::-1, :].diagonal(i) for i in range(-matrix.shape[0] + 1, matrix.shape[1])]

        # Now back to the original array to get the upper-left-to-lower-right diagonals,
        # starting from the right, so the range needed for shape (x,y) was y-1 to -x+1 descending.
        diags.extend(matrix.diagonal(i) for i in range(matrix.shape[1] - 1, -matrix.shape[0], -1))

        # Another list comp to convert back to Python lists from numpy arrays,
        # so it prints what you requested.
        return [n.tolist() for n in diags]

    def _generate_paylines(self) -> t.List[t.List[str]]:
        results = []
        for i, val in enumerate(PAYLINE_VALUES):
            generated = random.choices(''.join(PAY_TABLE.keys()),
                                       weights=list(val.weights.values()),
                                       k=NUM_COLUMNS)
            results.append(generated)
        return results

    def get_full_name(self, author) -> str:
        return f'{author.name}#{author.discriminator}'



def setup(bot):
    bot.add_cog(SlotsCog(bot))
