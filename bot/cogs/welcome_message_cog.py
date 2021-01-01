import logging

import discord
from discord import colour
import discord.ext.commands as commands

from bot.data.welcome_message_repository import WelcomeMessageRepository
from bot.consts import Colors
import bot.extensions as ext

log = logging.getLogger(__name__)

class WelcomeMessageCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
    
    @ext.group(pass_context= True, invoke_without_command= True)
    @commands.has_guild_permissions(administrator= True)
    @ext.long_help(
        'Allows for server admins to set a welcome message to be dmd to every new member'
    )
    @ext.short_help('Set a server welcome dm message')
    @ext.example('welcome')
    async def welcome(self, ctx):
        repo = WelcomeMessageRepository()
        message = await repo.get_welcome_message(ctx.guild.id)

        if not message:
            embed = discord.Embed(title= 'Error: This server has no welcome message', color= Colors.Error) 
            await ctx.send(embed= embed)
            return

        await ctx.send(message)

    @welcome.command()
    @commands.has_guild_permissions(administrator= True)
    @ext.long_help(
        'Sets a welcome message to be dmd to every new member'
    )
    @ext.short_help('Sets the welcome message')
    @ext.example('welcome set welcome to our amazing server')
    async def set(self, ctx, *, content):
        repo = WelcomeMessageRepository()
        await repo.set_welcome_message(ctx.guild, content)
        embed = discord.Embed(title= 'Server welcome message set  :white_check_mark:', color= Colors.ClemsonOrange)
        await ctx.send(embed= embed)


    @welcome.command( aliases = ['remove'])
    @commands.has_guild_permissions(administrator= True)
    @ext.long_help(
        'Allows for server admins to remove a welcome message from their server'
    )
    @ext.short_help('Removes the welcome message')
    @ext.example('welcome delete')
    async def delete(self, ctx):
        repo = WelcomeMessageRepository()

        message = await repo.get_welcome_message(ctx.guild.id)
        if not message:
            embed = discord.Embed(title= 'Error: This server has no welcome message', color= Colors.Error) 
            await ctx.send(embed= embed)
            return

        await repo.delete_welcome_message(ctx.guild)
        embed = discord.Embed(title= 'Server welcome message deleted  :white_check_mark:', color= Colors.ClemsonOrange)
        await ctx.send(embed= embed)
    
def setup(bot): 
    bot.add_cog(WelcomeMessageCog(bot))
