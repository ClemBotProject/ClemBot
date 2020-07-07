import logging

import discord
import discord.ext.commands as commands

log = logging.getLogger(__name__)


class ManageClassesCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self._last_member = None

    @commands.command()
    async def hello(self, ctx, *, member: discord.Member = None):
        member = member or ctx.author
        if self._last_member is None or self._last_member.id != member.id:
            await ctx.send('Hello {0.name}~'.format(member))
        else:
            await ctx.send('Hello {0.name}... This feels familiar.'.format(member))
        self._last_member = member

    @commands.command()
    async def echo(self, ctx, *message, member: discord.Member = None):
        embed = discord.Embed(title="Echo", color= 0x522D80)
        embed.add_field(name=ctx.author, value=' '.join(message))
        await ctx.send(embed=embed)

def setup(bot): 
    bot.add_cog(ManageClassesCog(bot))
