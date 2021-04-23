import logging
from operator import sub
import typing as t
from datetime import datetime, timedelta

import discord
import discord.ext.commands as commands

import bot.extensions as ext
from bot.consts import Claims, Colors, DesignatedChannels
from bot.utils.converters import Duration, DurationDelta
from bot.utils.user_choice import UserChoice
from bot.messaging.events import Events

log = logging.getLogger(__name__)

MUTE_ROLE_NAME = 'ClemBot Mute'

class MuteCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @ext.command()
    @ext.required_claims(Claims.moderation_mute)
    async def mute(self, ctx: commands.Context, time: DurationDelta, subject: discord.Member, *, reason: t.Optional[str]):

        duration_str = self._get_time_str(time)
        time = Duration().convert(ctx, time)

        if ctx.author.top_role.position <= subject.top_role.position:
            embed = discord.Embed(color=Colors.Error)
            embed.title = f'Error: Invalid Permissions'
            embed.add_field(name='Reason', value='Cannot moderate someone with the same rank or higher')
            embed.set_author(name=self.get_full_name(ctx.author), icon_url=ctx.author.avatar_url)
            return await ctx.send(embed=embed)
        
        mute_role = discord.utils.get(ctx.guild.roles, name=MUTE_ROLE_NAME)
        if not mute_role:
            get_input = UserChoice(ctx=ctx, timeout=30)
            choice = await get_input.send_confirmation(
                content= 'Error: Clembots Mute role not found. Would you like me to create it?',
                is_error=True)

            if not choice:
                embed = discord.Embed(color=Colors.Error)
                embed.title = f'Error: Mute Role not found, Cancelling operation'
                embed.set_author(name=self.get_full_name(ctx.author), icon_url=ctx.author.avatar_url)
                return
            
            mute_role = await ctx.guild.create_role(name=MUTE_ROLE_NAME)
            await mute_role.edit(position=ctx.guild.me.top_role.position-1)

            for channel in ctx.guild.channels:
                await channel.set_permissions(mute_role, 
                        speak=False, 
                        connect=False,
                        stream=False,
                        send_messages=False,
                        send_tts_messages=False,
                        add_reactions=False)
            embed = discord.Embed(color=Colors.ClemsonOrange)
            embed.title = f'@{MUTE_ROLE_NAME} Successfully Configured  :white_check_mark:'
            await ctx.send(embed=embed)
                
        await self.bot.messenger.publish(Events.on_bot_mute, 
                guild=ctx.guild,
                author=ctx.author,
                subject=subject,
                reason=reason)

        embed = discord.Embed(color=Colors.ClemsonOrange)
        embed.title = f'{self.get_full_name(subject)} Muted :white_check_mark:'
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

    def _get_time_str(self, elapsed):
        return f'{elapsed.days} Days {elapsed.hours} Hours {elapsed.minutes} Mins'



def setup(bot): 
    bot.add_cog(MuteCog(bot))
