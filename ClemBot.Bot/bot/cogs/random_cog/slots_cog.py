import asyncio
import dataclasses
import random
import typing as t
from collections import Counter
from datetime import datetime
from typing import List, Tuple, Union

import discord
import discord.ext.commands as commands
import numpy as np

import bot.extensions as ext
from bot.clem_bot import ClemBot
from bot.consts import Colors
from bot.models.guild_models import SlotScore
from bot.utils import helpers
from bot.utils.helpers import chunk_sequence
from bot.utils.logging_utils import get_logger


class Symbols:
    combined = "🍎🍐🍇🍊🍋🍓🍒💎"

    apple = "🍎"
    pear = "🍐"
    grape = "🍇"
    orange = "🍊"
    lemon = "🍋"
    cherry = "🍒"
    strawberry = "🍓"
    jackpot = "💎"


PAY_TABLE = {
    Symbols.apple: 1,
    Symbols.pear: 2,
    Symbols.grape: 10,
    Symbols.orange: 20,
    Symbols.lemon: 50,
    Symbols.cherry: 200,
    Symbols.strawberry: 1000,
    Symbols.jackpot: 5000,
}


@dataclasses.dataclass
class PayLine:
    multiplier: int
    weights: dict[str, float]


VERTICAL_MULTIPLIERS = {
    1: 1,
    2: 2,
    3: 10,
}

DIAGONAL_MULTIPLIERS = {1: 1, 2: 1, 3: 3}

HORIZONTAL_MULTIPLIERS = {1: 1, 2: 2, 3: 7, 4: 20, 5: 50}

NUM_COLUMNS = 5
COLUMN_HEADERS = ["1️⃣", "2️⃣", "3️⃣", "2️⃣", "1️⃣"]

NUM_ROWS = 3
ROW_HEADERS = ["1️⃣", "4️⃣", "2️⃣"]

PAYLINE_VALUES = [
    PayLine(
        multiplier=1,
        weights={
            Symbols.apple: 115,
            Symbols.pear: 80,
            Symbols.grape: 75,
            Symbols.orange: 50,
            Symbols.lemon: 25,
            Symbols.cherry: 10,
            Symbols.strawberry: 5,
            Symbols.jackpot: 3,
        },
    ),
    PayLine(
        multiplier=4,
        weights={
            Symbols.apple: 150,
            Symbols.pear: 100,
            Symbols.grape: 80,
            Symbols.orange: 65,
            Symbols.lemon: 27,
            Symbols.cherry: 10,
            Symbols.strawberry: 5,
            Symbols.jackpot: 2,
        },
    ),
    PayLine(
        multiplier=2,
        weights={
            Symbols.apple: 100,
            Symbols.pear: 80,
            Symbols.grape: 75,
            Symbols.orange: 50,
            Symbols.lemon: 20,
            Symbols.cherry: 10,
            Symbols.strawberry: 5,
            Symbols.jackpot: 2,
        },
    ),
]

COLUMN_MULTIPLIERS = [1, 2, 3, 2, 1]

PHRASES_PATH = "bot/cogs/random_cog/assets/phrases.txt"

log = get_logger(__name__)
SLOTS_COMMAND_COOLDOWN = 60


class SlotsCog(commands.Cog):
    def __init__(self, bot: ClemBot) -> None:
        self.bot = bot

    async def format_board_embed(
        self, ctx: ext.ClemBotCtx, scores: List[SlotScore], title: str, emoji: str
    ) -> discord.Embed:
        embed = discord.Embed(title=title, colour=Colors.ClemsonOrange)

        if len(scores) == 0:
            embed.add_field(name="Scores", value="No scores found.")
        for i, score in enumerate(scores):
            user = await self.bot.fetch_user(score.user_id)

            if not user:
                continue
            msg = f"Achieved on {score.time_occurred.strftime('%B %d, %Y')}"
            if score.message_id and score.channel_id:
                msg += f" [here](https://discord.com/channels/{ctx.guild.id}/{score.channel_id}/{score.message_id})"
            embed.add_field(
                name=f"{emoji} {i + 1: >3}. {user.name} - {score.high_score}",
                value=msg + "\n",
                inline=False,
            )

        embed.set_footer(text=str(ctx.author), icon_url=ctx.author.display_avatar.url)
        return embed

    @ext.group(aliases=["slotmachine"], invoke_without_command=True, case_insensitive=True)
    @commands.cooldown(1, SLOTS_COMMAND_COOLDOWN, commands.BucketType.user)
    @ext.long_help("A slot machine inside discord with a chance to win fame and fortune")
    @ext.short_help("How lucky are you?")
    @ext.example("slots")
    async def slots(self, ctx: ext.ClemBotCtx) -> None:
        paylines = self._generate_paylines()

        score = self._calculate_score(np.array(paylines))

        embed, msg = await self._render_slots_embed(ctx, paylines, score[0])  # type: ignore

        # Wait a second before showing the score
        await asyncio.sleep(1)
        embed.add_field(name="**SCORE!!**", value=score[1], inline=False)
        await msg.edit(embed=embed)

        await self.bot.slots_score_route.add_slot_score(
            score[1], ctx.guild.id, ctx.author.id, msg.id, msg.channel.id
        )

    @slots.command(aliases=["top", "winners"])
    async def leaderboard(self, ctx: ext.ClemBotCtx) -> None:
        scores = await self.bot.guild_route.get_guild_slot_scores(ctx.guild.id, 10, True)

        await ctx.send(
            embed=await self.format_board_embed(
                ctx, scores, "💎 ClemBot Slot Machine Leaderboard 💎", "👑"
            )
        )

    @slots.command(aliases=["bottom", "losers"])
    async def loserboard(self, ctx: ext.ClemBotCtx) -> None:
        scores = await self.bot.guild_route.get_guild_slot_scores(ctx.guild.id, 10, False)

        await ctx.send(
            embed=await self.format_board_embed(
                ctx, scores, "💩 ClemBot Slot Machine Loserboard 💩", "🤡"
            )
        )

    def _calculate_score(
        self, paylines: np.ndarray[t.Any, t.Any]
    ) -> tuple[list[str | list[str]], int]:

        winning_groups = []

        # Calculate the horizontal scores, while counting groupings of one
        horizontal_score = 0
        for i, line in enumerate(paylines):
            groups = self._calculate_line_score(
                results=line,
                consecutive_multipliers=HORIZONTAL_MULTIPLIERS,
                count_singles=True,
                payline_multiplier=PAYLINE_VALUES[i].multiplier,
            )
            horizontal_score += groups[1]
            winning_groups.extend(groups[0])

        # Transpose the matrix to easily check for vertical groupings
        flipped_arr = np.rot90(paylines)
        vertical_score = 0
        for i, line in enumerate(flipped_arr):
            groups = self._calculate_line_score(
                results=line,
                consecutive_multipliers=VERTICAL_MULTIPLIERS,
                count_singles=False,
                payline_multiplier=COLUMN_MULTIPLIERS[i],
            )
            vertical_score += groups[1]
            winning_groups.extend(groups[0])

        # Grab diagonals with a length greater than one and check for more groupings
        diagonals = self._get_all_diagonals(paylines)
        diagonals = [d for d in diagonals if len(d) > 1]

        diagonal_score = 0
        for i, line in enumerate(diagonals):
            groups = self._calculate_line_score(
                results=line, count_singles=False, consecutive_multipliers=DIAGONAL_MULTIPLIERS
            )
            diagonal_score += groups[1]
            winning_groups.extend(groups[0])

        return winning_groups, horizontal_score + vertical_score + diagonal_score

    def _calculate_line_score(
        self,
        *,
        results: list[str],
        count_singles: bool,
        consecutive_multipliers: dict[int, int],
        payline_multiplier: int = 1,
    ) -> tuple[list[str | list[str]], int]:

        groups: list[list[str] | str] = []
        curr_group: list[str] = []

        for i, val in enumerate(results):
            if val in curr_group or len(curr_group) == 0:
                curr_group.append(val)
            elif i == len(results):
                groups.append(val)
            else:
                groups.append(curr_group)
                curr_group = [val]

        groups.append(curr_group)

        # Only count single jackpots on the horizontal pass
        if not count_singles:
            groups = [g for g in groups if len(g) > 1]

        total_score = 0
        for i, g in enumerate(groups):
            total_score += (
                PAY_TABLE[g[0]] * len(g) * consecutive_multipliers[len(g)] * payline_multiplier
            )

        return groups, total_score

    def _get_all_diagonals(self, matrix: np.ndarray[t.Any, t.Any]) -> list[list[t.Any]]:
        """https://stackoverflow.com/a/6313414"""
        diags = [matrix[::-1, :].diagonal(i) for i in range(-matrix.shape[0] + 1, matrix.shape[1])]

        # Now back to the original array to get the upper-left-to-lower-right diagonals,
        # starting from the right, so the range needed for shape (x,y) was y-1 to -x+1 descending.
        diags.extend(matrix.diagonal(i) for i in range(matrix.shape[1] - 1, -matrix.shape[0], -1))

        # Another list comp to convert back to Python lists from numpy arrays,
        # so it prints what you requested.
        return [n.tolist() for n in diags]

    def _generate_paylines(self) -> list[list[str]]:
        results = []
        for i, val in enumerate(PAYLINE_VALUES):
            generated = random.choices(
                "".join(PAY_TABLE.keys()), weights=list(val.weights.values()), k=NUM_COLUMNS
            )
            results.append(generated)
        return results

    async def _render_slots_embed(
        self, ctx: ext.ClemBotCtx, paylines: list[list[str]], winning_groups: list[list[str]]
    ) -> tuple[discord.Embed, discord.Message]:

        slots_title = "💎 ClemBot Slot Machine 💎"
        prefix = await self.bot.current_prefix(ctx)

        with open(PHRASES_PATH) as f:
            quote = random.choice(f.readlines())

        def slots_rolling(iter: int) -> discord.Embed:
            embed = discord.Embed(title=slots_title, description=quote, colour=Colors.ClemsonOrange)

            embed.add_field(
                name=self._render_board(paylines, iter), value="Spinning!!!", inline=False
            )
            embed.set_footer(
                text=f"{ctx.author}\nTo view the leaderboard run {prefix}slots leaderboard\nTo view the loserboard run {prefix}slots loserboard\n",
                icon_url=ctx.author.display_avatar.url,
            )
            return embed

        msg = await ctx.send(embed=slots_rolling(0))

        for i in range(NUM_COLUMNS + NUM_ROWS):
            embed = slots_rolling(i)
            await msg.edit(embed=embed)
            await asyncio.sleep(1)

        winning_counts = Counter(tuple(g) for g in winning_groups)
        items = list(winning_counts.items())
        items.sort(reverse=True, key=lambda k: len(k[0]))
        for chunk in chunk_sequence(items, 4):
            embed.add_field(
                name="Winning Groups!",
                value="\n".join(f'{", ". join(k)} x{v}' for k, v in chunk),
                inline=True,
            )

        # Send the final embed with groups included and return the embed so score can be added
        await msg.edit(embed=embed)

        return embed, msg

    def _render_board(self, paylines: list[list[str]], iter_num: int = 3) -> str:

        # Generate empty game-board
        game_board = [["◻️" for _ in range(NUM_COLUMNS)] for _ in range(NUM_ROWS)]

        # Generate the animation frame based on the iteration number
        # This uses the row number as the column offset
        for i in range(NUM_ROWS):
            for j in range(iter_num):
                try:
                    # Check if the offset is less then zero, if it is we
                    # cant access that part of the array so skip it
                    if j - i < 0:
                        continue
                    game_board[i][j - i] = paylines[i][j - i]
                except:
                    # Bare except to account for out of position offsets
                    # which is expected as the animation hits the end
                    pass

        board = [["0️⃣️", *COLUMN_HEADERS]]

        for i in range(NUM_ROWS):
            board.append([ROW_HEADERS[i], *game_board[i]])

        val = "\n".join(f'` `{" | ".join(row)}` `' for row in board)

        return val


async def setup(bot: ClemBot) -> None:
    await bot.add_cog(SlotsCog(bot))
