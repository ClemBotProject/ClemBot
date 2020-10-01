import random
import discord
import discord.ext.commands as commands
from bot.consts import Colors

class DiceRollCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases = ['roll','dice'])
    async def diceroll(self, ctx, dice : str):
        """
        Rolls dice in a XdY format where X is the number of dice and Y is the number of sides on the dice.
            Example:
            1d6     -   Rolls 1 die with 6 sides
            2d8     -   Rolls 2 die with 8 sides
            3d10    -   Rolls 3 die with 10 sides
            4d20    -   Rolls 4 die with 20 sides
        """
        try:
            rolls, limit = map(int, dice.split('d'))
        except Exception:
            await ctx.send('Entry has to be in a XdY format! See the help command for an example.')
            return

        result = ', '.join(str(random.randint(1, limit)) for r in range(rolls))

        embed = discord.Embed(title ='Dice Roller', description = f'{ctx.message.author.mention} rolled {dice}', color = Colors.ClemsonOrange)
        embed.add_field(name ='Here are the results of their rolls: ', value = result, inline = False)
        await ctx.send(embed = embed)

def setup(bot):
    bot.add_cog(DiceRollCog(bot))
