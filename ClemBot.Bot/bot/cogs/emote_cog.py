import logging

import aiohttp
import discord
import discord.ext.commands as commands

import bot.extensions as ext
from bot.consts import Colors, Claims

log = logging.getLogger(__name__)


class EmoteCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @ext.group(hidden=True, aliases=['emoji'])
    async def emote(self, ctx):
        pass

    @emote.command()
    @ext.required_claims(Claims.emote_add)
    async def add(self, ctx: commands.Context, emote, name: str):
        emote_id = emote.split(':')[2][:-1]
        async with aiohttp.ClientSession() as session:
            async with session.get(f'https://cdn.discordapp.com/emojis/{emote_id}.png?v=1') as resp:
                test = await resp.read()

        emote = await ctx.guild.create_custom_emoji(name=name, image=test)

        log.info(f'Emote added in guild: {ctx.guild.id}, name: {emote.name}, by: {ctx.author.id}')

        embed = discord.Embed(title='Emoji successfully created :white_check_mark:', color=Colors.ClemsonOrange)
        embed.add_field(name='Name:', value=f'```{emote.name}```')

        embed.set_thumbnail(url=emote.url)

        fullName = f'{ctx.author.name}#{ctx.author.discriminator}'
        embed.set_footer(text=f'Created By: {fullName}', icon_url=ctx.author.avatar_url)
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(EmoteCog(bot))
