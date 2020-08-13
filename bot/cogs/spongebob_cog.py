import random
import os
import time

import logging
import random


import discord
import discord.ext.commands as commands

from bot.consts import Colors

log = logging.getLogger(__name__)

class spongebobCog(commands.Cog):
    
    def __init__(self, bot):
        self.bot=bot
        self.upperThreshold = 100
        self.lowerThreshold = 0

    @commands.command()
    async def spongebob(self, ctx, *, args):

        '''
        Spongebob Text
        '''
        random.seed(time.time())

    
        args = args.replace('"', "'")
        

        result = ''
        for i in args:
            helper = random.randint(self.lowerThreshold,self.upperThreshold)
            
            if helper > self.upperThreshold//2:
                result += str(i).upper()
            else:
                result += str(i).lower()

        embed = discord.Embed(title="SpOnGeBoB", color=Colors.ClemsonOrange)

        result2 = ''
        if len(result) >= 1024:
            result2 = result[1024:len(result)]
            result = result[:1023]
        embed.add_field(name="TeXt", value=result, inline=False)
        if result2:
            print("RESULT2\n\n\n")
            embed.add_field(name="tExT", value=result2, inline=False)


        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(spongebobCog(bot))