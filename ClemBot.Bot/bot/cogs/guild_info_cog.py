import arrow
import asyncio
import discord
from discord.ext import commands

import bot.extensions as ext
from bot.consts import Colors

class GuildInfoCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @ext.command()
    @ext.long_help('Shows information on the current guild/Discord server.')
    @ext.short_help('Shows info on a Discord server.')
    @ext.example('guildinfo')
    async def guildinfo(self, ctx, guild: discord.Guild = None):
        guild = ctx.guild

        embed = discord.Embed(color=Colors.ClemsonOrange, title=f'{guild.name} Information [{guild.id}]')
        embed.set_thumbnail(url=guild.icon_url)
        
        member_count = len([m for m in guild.members if not m.bot])
        bot_count = len([m for m in guild.members if m.bot])
        channel_count = len(guild.text_channels) + len(guild.voice_channels)  # excludes categories
        formatted_roles = ' '.join(reversed([r.mention for r in guild.roles if r.id != guild.id]))
        age = arrow.get(guild.created_at)
        display_age = f"{age.format('MMM D, YYYY')}, {age.humanize()}"

        # try:
        #     ban_count = len(await asyncio.wait_for(guild.bans(), 1))
        # except asyncio.TimeoutError:  # so many bans, eeee
        #     ban_count = 'unknown'

        base = '» **{}:** {}'

        embed.description = '\n'.join([
            base.format('Created At', display_age),
            base.format('Owner', guild.owner.mention),
            base.format('Member Count', member_count),
            base.format('Bot Count', bot_count),
            # base.format('Ban Count', ban_count),
            base.format('Channel Count', channel_count),
            base.format('Roles', formatted_roles),
        ])

        embed.set_footer(text=str(ctx.author), icon_url=ctx.author.display_avatar.url)

        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(GuildInfoCog(bot))
