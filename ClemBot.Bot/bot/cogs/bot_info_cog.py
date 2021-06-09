import discord
from discord.ext import commands

import bot.extensions as ext
from bot.consts import Colors


class InviteCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @ext.command()
    @ext.long_help(
        'My invite link so you can invite me to your server!'
    )
    @ext.short_help('Shows my invite link')
    @ext.example('invite')
    async def invite(self, ctx):
        embed = discord.Embed(color=Colors.ClemsonOrange)
        embed.title = 'Here is my invite link!  :grin:'
        embed.description = 'Add me to your server!'
        embed.add_field(name='Link',
                        value='[Click me!](https://discord.com/api/oauth2/authorize?client_id=710672266245177365&permissions=1409412343&scope=bot)')
        embed.add_field(name='Resources',
                        value='For information on advanced features\nplease see my wiki\n[Link!](https://github.com/ClemsonCPSC-Discord/ClemBot/wiki)')
        embed.set_thumbnail(url=self.bot.user.avatar_url_as(static_format='png'))
        await ctx.send(embed=embed)

    @ext.command()
    @ext.long_help(
        'Shows information about me and my owner!'
    )
    @ext.short_help('Provides bot info')
    @ext.example('about')
    async def about(self, ctx: commands.Context):
        owner = self.bot.get_user(self.bot.owner_id)

        embed = discord.Embed(color=Colors.ClemsonOrange)
        embed.description = f'{len(self.bot.guilds)} Guilds\n{len(self.bot.users)} Users'
        embed.title = f'{self.bot.user.name}#{self.bot.user.discriminator}'
        embed.add_field(name='Owner', value=owner.mention)
        embed.add_field(name='Repository', value='[Link!](https://github.com/ClemsonCPSC-Discord/ClemBot)')
        embed.add_field(name='Wiki', value='[Link!](https://github.com/ClemsonCPSC-Discord/ClemBot/wiki)')
        embed.set_thumbnail(url=self.bot.user.avatar_url_as(static_format='png'))
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(InviteCog(bot))
