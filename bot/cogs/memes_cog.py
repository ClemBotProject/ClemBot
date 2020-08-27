import logging

import discord
import discord.ext.commands as commands

import random
import time

from bot.consts import Colors

log = logging.getLogger(__name__)

class MemesCog(commands.Cog):

    
    max_waldo_grid_size = 100

    def __init__(self, bot):
        self.bot = bot
    
    @commands.command()
    async def bubblewrap(self, ctx):

        msg = ''
        for i in range(0, 5):
            for j in range(0, 10):
                msg += '||pop!|| '
            msg += '\n'

        await ctx.send(msg)

    @commands.command()
    async def Waldo(self, ctx, size=max_waldo_grid_size):

        max_waldo_line_size = 6
        new_line_waldo_chance = 10
        msg = ''
        count = 0
        place = random.randint(0,size)

        for i in range(size+1):
            if i == place:
                msg += '||WALDO|| '
                count += 1
            else:
                msg += '||MALDO|| '
                count += 1
            new_line = random.randint(0,100)
            if new_line < new_line_waldo_chance or count > max_waldo_line_size:
                msg += '\n'
                count = 0

        await ctx.send(msg)

    @commands.command()
    async def spongebob(self, ctx, *, args):

        '''
        Spongebob Text
        '''
        random.seed(time.time())
        args = args.replace('"', "'")
    
        result = ''
        for i in args:
            helper = random.randint(0, 100)
            
            if helper > 60:
                result += str(i).upper()
            else:
                result += str(i).lower()

        embed = discord.Embed(title="SpOnGeBoB", color=Colors.ClemsonOrange)
        result2 = ''

        # Discord messages can only be 2k characters long, this block accounts for that
        if len(result) >= 1024:
            result2 = result[1024:len(result)]
            result = result[:1023]
        embed.add_field(name="TeXt", value=result, inline=False)

        if result2:
            embed.add_field(name="tExT", value=result2, inline=False)
        

        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(MemesCog(bot))