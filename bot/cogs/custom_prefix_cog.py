import logging

import discord
from discord import embeds
import discord.ext.commands as commands

from bot.messaging.events import Events
from bot.bot_secrets import BotSecrets
from bot.data.custom_prefixes_repository import CustomPrefixesRepository
from bot.consts import Colors
log = logging.getLogger(__name__)


class CustomPrefixCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
    
    @commands.group(pass_context= True, aliases= ['prefixs'])
    async def prefix(self, ctx):
        pass
    
    @prefix.command(pass_context= True, aliases= ['add'])
    @commands.has_guild_permissions(administrator= True)
    async def set(self, ctx, prefix: str):

        if await self.bot.get_prefix(ctx.message) == prefix:
            embed = discord.Embed(title= 'Error', color= Colors.Error)
            embed.add_field(name= 'Invalid prefix', value= f'"{prefix}" is already the prefix for this guild')
            await ctx.send(embed= embed)
            return
        
        if '`' in prefix:
            embed = discord.Embed(title= 'Error', color= Colors.Error)
            embed.add_field(name= 'Invalid prefix', value= 'Prefix can not contain " ` "')
            await ctx.send(embed= embed)
            return

        repo = CustomPrefixesRepository()
        await repo.set_prefix(ctx.guild.id, prefix)
        await self.bot.messenger.publish(Events.on_set_custom_prefix, ctx.guild, prefix)

        embed = discord.Embed(color= Colors.ClemsonOrange)
        embed.add_field(name= 'Prefix changed   :white_check_mark:', value= f'New Prefix: ```{prefix}```')
        await ctx.send(embed= embed)
        
    @prefix.command(pass_context= True, aliases= ['revert'])
    @commands.has_guild_permissions(administrator= True)
    async def reset(self, ctx):

        default_prefix = BotSecrets.get_instance().bot_prefix

        if await self.bot.get_prefix(ctx.message) == default_prefix:
            embed = discord.Embed(title= 'Error', color= Colors.Error)
            embed.add_field(name= 'Invalid prefix', value= f'"{default_prefix}" Prefix is already the default')
            await ctx.send(embed= embed)
            return

        repo = CustomPrefixesRepository()

        await repo.set_prefix(ctx.guild.id, default_prefix)
        await self.bot.messenger.publish(Events.on_set_custom_prefix, ctx.guild, default_prefix)

        embed = discord.Embed(color= Colors.ClemsonOrange)
        embed.add_field(
            name= 'Prefix reset   :white_check_mark:',
            value= f'New Prefix: ```{default_prefix}```')

        await ctx.send(embed= embed)
def setup(bot): 
    bot.add_cog(CustomPrefixCog(bot))