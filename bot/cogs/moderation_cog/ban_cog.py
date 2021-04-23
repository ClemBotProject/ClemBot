import logging
import typing as t

import discord
import discord.ext.commands as commands

import bot.extensions as ext
from bot.consts import Claims, Colors, DesignatedChannels
from bot.messaging.events import Events

log = logging.getLogger(__name__)


class BanCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @ext.command()
    @ext.required_claims(Claims.moderation_ban)
    async def ban(self, ctx: commands.Context, subject: discord.Member, *, reason: str):

        if ctx.author.roles[-1].position <= subject.roles[-1].position:
            embed = discord.Embed(color=Colors.Error)
            embed.title = f'Error: Invalid Permissions'
            embed.add_field(name='Reason', value='Cannot moderate someone with the same rank or higher')
            embed.set_author(name=self.get_full_name(ctx.author), icon_url=ctx.author.avatar_url)
            return await ctx.send(embed=embed)

        await self.bot.messenger.publish(Events.on_bot_ban, 
                guild=ctx.guild,
                author=ctx.author,
                subject=subject,
                reason=reason)

        embed = discord.Embed(color=Colors.ClemsonOrange)
        embed.title = f'{self.get_full_name(subject)} Banned  :white_check_mark:'
        embed.set_author(name=self.get_full_name(ctx.author), icon_url=ctx.author.avatar_url)
        embed.set_thumbnail(url= subject.avatar_url_as(static_format= 'png'))
        embed.description = reason

        await ctx.send(embed=embed)

        embed = discord.Embed(color=Colors.ClemsonOrange)
        embed.title = 'Guild Member Banned  :hammer:'
        embed.set_author(name=self.get_full_name(ctx.author), icon_url=ctx.author.avatar_url)
        embed.add_field(name='Name', value=self.get_full_name(subject))
        embed.add_field(name='Id', value=subject.id)
        embed.add_field(name='Reason', value=f'```{reason}```', inline=False)
        embed.add_field(name='Message Link', value=f'[Link]({ctx.message.jump_url})')
        embed.set_thumbnail(url= subject.avatar_url_as(static_format= 'png'))

        await self.bot.messenger.publish(Events.on_send_in_designated_channel, 
                DesignatedChannels.moderation_log,
                ctx.guild.id,
                embed)
    
    def get_full_name(self, author) -> str: 
        return f'{author.name}#{author.discriminator}' 

def setup(bot): 
    bot.add_cog(BanCog(bot))
