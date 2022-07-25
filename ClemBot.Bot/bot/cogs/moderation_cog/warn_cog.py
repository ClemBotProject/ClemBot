import logging

import discord
import discord.ext.commands as commands
import seqlog

import bot.extensions as ext
from bot.consts import Claims, Colors, DesignatedChannels
from bot.messaging.events import Events
from bot.clem_bot import ClemBot

log: seqlog.StructuredLogger = logging.getLogger(__name__)  # type: ignore


class WarnCog(commands.Cog):

    def __init__(self, bot: ClemBot):
        self.bot = bot

    @ext.command()
    @ext.long_help(
        'Warns a user and applies an infraction to them'
    )
    @ext.short_help('Warns a user')
    @ext.example('warn @SomeUser an example warning')
    @ext.required_claims(Claims.moderation_mute)
    @ext.required_claims(Claims.moderation_warn)
    async def warn(self, ctx: commands.Context[ClemBot], subject: discord.Member, *, reason: str):
        ctx.author: discord.Member

        if ctx.author.roles[-1].position <= subject.roles[-1].position:
            embed = discord.Embed(color=Colors.Error)
            embed.title = 'Error: Invalid Permissions'
            embed.add_field(name='Reason', value='Cannot moderate someone with the same rank or higher')
            embed.set_author(name=str(ctx.author), icon_url=ctx.author.display_avatar.url)
            return await ctx.send(embed=embed)

        # Log the warning first so if it throws we notify and dont dm people
        await self.bot.messenger.publish(Events.on_bot_warn,
                                         guild=ctx.guild,
                                         author=ctx.author,
                                         subject=subject,
                                         reason=reason)

        # Dm the user who was warned
        embed = discord.Embed(color=Colors.ClemsonOrange)
        embed.title = f'You have been warned in Guild {ctx.guild.name}  :warning:'
        embed.set_author(name=str(ctx.author), icon_url=ctx.author.display_avatar.url)
        embed.set_thumbnail(url=str(ctx.guild.icon.url))
        embed.add_field(name='Reason :page_facing_up:', value=f'```{reason}```', inline=False)
        embed.description = f'**Guild:** {ctx.guild.name}'

        try:
            await subject.send(embed=embed)
        except (discord.Forbidden, discord.HTTPException):
            embed = discord.Embed(color=Colors.ClemsonOrange)
            embed.title = f'Dm Warn to {subject} forbidden'
            await self.bot.messenger.publish(Events.on_send_in_designated_channel,
                                             DesignatedChannels.moderation_log,
                                             ctx.guild.id,
                                             embed)


        embed = discord.Embed(color=Colors.ClemsonOrange)
        embed.title = f'{subject} Warned  :warning:'
        embed.set_author(name=str(ctx.author), icon_url=ctx.author.display_avatar.url)
        embed.set_thumbnail(url=subject.display_avatar.url)
        embed.description = reason

        await ctx.send(embed=embed)

        embed = discord.Embed(color=Colors.ClemsonOrange)
        embed.title = 'Guild Member Warned  :warning:'
        embed.set_author(name=f'{ctx.author}\nId: {ctx.author.id}', icon_url=ctx.author.display_avatar.url)
        embed.add_field(name=str(subject), value=f'Id: {subject.id}')
        embed.add_field(name='Reason :page_facing_up:', value=f'```{reason}```', inline=False)
        embed.add_field(name='Message Link  :rocket:', value=f'[Link]({ctx.message.jump_url})')
        embed.set_thumbnail(url=subject.display_avatar.url)

        await self.bot.messenger.publish(Events.on_send_in_designated_channel,
                                         DesignatedChannels.moderation_log,
                                         ctx.guild.id,
                                         embed)


def setup(bot):
    bot.add_cog(WarnCog(bot))
