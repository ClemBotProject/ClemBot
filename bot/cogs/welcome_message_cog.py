import logging

import discord
import discord.ext.commands as commands

import bot.extensions as ext
from bot.consts import Colors, Claims
from bot.data.welcome_message_repository import WelcomeMessageRepository

log = logging.getLogger(__name__)


class WelcomeMessageCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @ext.group(case_insensitive=True, invoke_without_command=True)
    @ext.required_claims(Claims.welcome_message_view)
    @ext.long_help(
        'Allows for server admins to set a welcome message to be dmd to every new member'
    )
    @ext.short_help('Set a server welcome dm message')
    @ext.example('welcome')
    async def welcome(self, ctx):
        repo = WelcomeMessageRepository()
        message = await repo.get_welcome_message(ctx.guild.id)

        if not message:
            embed = discord.Embed(title='Error: This server has no welcome message', color=Colors.Error)
            await ctx.send(embed=embed)
            return

        await ctx.send(message)

    @welcome.command()
    @ext.required_claims(Claims.welcome_message_modify)
    @ext.long_help(
        'Sets a welcome message to be dmd to every new member'
    )
    @ext.short_help('Sets the welcome message')
    @ext.example('welcome set welcome to our amazing server')
    async def set(self, ctx, *, content):
        repo = WelcomeMessageRepository()
        await repo.set_welcome_message(ctx.guild, content)
        embed = discord.Embed(title='Server welcome message set  :white_check_mark:', color=Colors.ClemsonOrange)
        await ctx.send(embed=embed)

    @welcome.command(aliases=['remove'])
    @ext.required_claims(Claims.welcome_message_modify)
    @ext.long_help(
        'Allows for server admins to remove a welcome message from their server'
    )
    @ext.short_help('Removes the welcome message')
    @ext.example('welcome delete')
    async def delete(self, ctx):
        repo = WelcomeMessageRepository()

        message = await repo.get_welcome_message(ctx.guild.id)
        if not message:
            embed = discord.Embed(title='Error: This server has no welcome message', color=Colors.Error)
            await ctx.send(embed=embed)
            return

        await repo.delete_welcome_message(ctx.guild)
        embed = discord.Embed(title='Server welcome message deleted  :white_check_mark:', color=Colors.ClemsonOrange)
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(WelcomeMessageCog(bot))
