import asyncio
import enum

from discord.ext import commands
import discord

from bot.clem_bot import ClemBot
from bot.consts import Colors
from bot.messaging.events import Events
import bot.extensions as ext


class RpsChoice(enum.Enum):
    ROCK = enum.auto()
    PAPER = enum.auto()
    SCISSORS = enum.auto()


ROCK_EMOJI = "🪨"
PAPER_EMOJI = "📜"
SCISSORS_EMOJI = "✂️"
FIRE_EMOJI = "🔥"

EMOJI_TO_CHOICE = {
    ROCK_EMOJI: RpsChoice.ROCK,
    PAPER_EMOJI: RpsChoice.PAPER,
    SCISSORS_EMOJI: RpsChoice.SCISSORS,
}

CHOICE_TO_EMOJI = dict(map(reversed, EMOJI_TO_CHOICE.items()))

WIN_MAP = [RpsChoice.ROCK, RpsChoice.SCISSORS, RpsChoice.PAPER]


class RockPaperScissorsCog(commands.Cog):
    def __init__(self, bot: ClemBot):
        self.bot = bot

    @staticmethod
    async def add_rps_reactions(msg: discord.Message) -> None:
        for emoji in EMOJI_TO_CHOICE:
            await msg.add_reaction(emoji)

    async def remove_rps_reactions(self, msg: discord.Message) -> None:
        await asyncio.wait([msg.remove_reaction(e, self.bot.user) for e in EMOJI_TO_CHOICE])

    async def rps_select(self, msg: discord.Message) -> RpsChoice:
        """Helper which waits for a user to react with one of the RPS emojis and returns their choice"""

        def check(r: discord.Reaction, u: discord.User) -> bool:
            return str(r.emoji) in EMOJI_TO_CHOICE and r.message == msg and u != self.bot.user
        
        try:
            r, u = await self.bot.wait_for("reaction_add", check=check, timeout=60)
        finally:
            try:
                await self.remove_rps_reactions(msg)
            except discord.HTTPException:
                pass

        await msg.edit(embed=discord.Embed(color=Colors.ClemsonOrange, description=f"You chose {r.emoji}"))

        return EMOJI_TO_CHOICE[str(r.emoji)]

    @ext.command(name="rps")
    @ext.long_help("Play rock paper scissors in Discord!")
    @ext.short_help("Play rock paper scissors in Discord!")
    @ext.example("rps @bozo")
    async def rock_paper_scissors(self, ctx: commands.Context, user_2: discord.Member):
        user_1 = ctx.author

        if user_1 == user_2:
            await ctx.send("You can't play rock paper scissors with yourself.")
            return

        embed = discord.Embed(color=Colors.ClemsonOrange, title="Rock Paper Scissors!", description=f"*React with {FIRE_EMOJI} to accept the challenge, {user_2.mention}*")
        embed.set_footer(text=str(ctx.author), icon_url=ctx.author.display_avatar.url)
        msg = await ctx.send(embed=embed)
        await msg.add_reaction(FIRE_EMOJI)

        # wait for challenge accept reaction from user_2
        try:
            await self.bot.wait_for("reaction_add", check=(lambda r, u: str(r.emoji) == FIRE_EMOJI and u == user_2 and r.message == msg), timeout=120)
        except asyncio.TimeoutError:
            msg: discord.Message = await msg.edit(f"Timed-out while waiting for {user_2.mention} to accept...", embed=None)

            try:
                await msg.remove_reaction(FIRE_EMOJI, ctx.me)
            except discord.HTTPException:
                pass

            await self.bot.messenger.publish(Events.on_set_deletable, msg=msg, author=ctx.author)
            return

        embed.description = "Waiting on users to select their choices..."

        await asyncio.gather(
            msg.clear_reaction(FIRE_EMOJI),
            msg.edit(embed=embed),
            return_exceptions=True,
        )
        
        embed = discord.Embed(color=Colors.ClemsonOrange, title="Rock Paper Scissors", description=f"*react with {ROCK_EMOJI}, {PAPER_EMOJI}, or {SCISSORS_EMOJI}*")

        async with ctx.typing():
            # send the choice select messages to both users
            try:
                user_1_msg, user_2_msg = await asyncio.gather(user_1.send(embed=embed), user_2.send(embed=embed))
            except discord.HTTPException:
                await msg.edit("Unable to send both users a direct message, which is required to play rock paper scissors.", embed=None)
                await self.bot.messenger.publish(Events.on_set_deletable, msg=msg, author=ctx.author)
                return

            # add the rps reactions to those messages
            await asyncio.wait([self.add_rps_reactions(user_1_msg), self.add_rps_reactions(user_2_msg)])
        
            # await their choices
            try:
                user_1_choice, user_2_choice = await asyncio.gather(
                    self.rps_select(user_1_msg),
                    self.rps_select(user_2_msg),
                )
            except asyncio.TimeoutError: # handle if someone doesn't pick something within a minute
                embed = discord.Embed(color=Colors.ClemsonOrange, description="Timed-out while waiting for users to react...")
                await msg.edit(embed=embed)
                return

        user_choices_str = f"{user_1.mention} chose {CHOICE_TO_EMOJI[user_1_choice]}, {user_2.mention} chose {CHOICE_TO_EMOJI[user_2_choice]}"

        def win_embed(user: discord.User) -> discord.Embed:
            return discord.Embed(color=Colors.ClemsonOrange, title=f"{user.display_name} won!", description=user_choices_str)
        
        if WIN_MAP[((WIN_MAP.index(user_1_choice) + 1) % len(WIN_MAP))] == user_2_choice:
            # user 1 win
            embed = win_embed(user_1)
        elif WIN_MAP[((WIN_MAP.index(user_2_choice) + 1) % len(WIN_MAP))] == user_1_choice:
            # user 2 win
            embed = win_embed(user_2)
        else:
            # tie
            embed = discord.Embed(color=Colors.ClemsonOrange, title="It's a tie!", description=user_choices_str)

        await msg.delete()
        await ctx.send(f"{user_1.mention} {user_2.mention}", embed=embed)


def setup(bot):
    bot.add_cog(RockPaperScissorsCog(bot))
