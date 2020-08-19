import logging

import discord
import discord.ext.commands as commands

import random
import time

from bot.consts import Colors

log = logging.getLogger(__name__)

class MemesCog(commands.Cog):

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