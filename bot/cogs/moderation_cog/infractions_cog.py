import logging
import typing as t
from datetime import datetime

import discord
import discord.ext.commands as commands

import bot.extensions as ext
from bot.consts import Claims, Colors
from bot.data.moderation_repository import ModerationRepository
from bot.messaging.events import Events

log = logging.getLogger(__name__)

INFRACTION_EMOJI_MAP = {
    'warn': ':warning:',
    'mute': ':mute:',
    'ban': ':hammer:'
}


class InfractionsCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @ext.group(case_insensitive=True, invoke_without_command=True, aliases=['infraction', 'warnings'])
    @ext.long_help(
        'Lists infractions for yourself or for a given user in the guild'
    )
    @ext.short_help('Lists a users infractions')
    @ext.example(('infractions', 'infractions @SomeUser'))
    @ext.required_claims(Claims.moderation_infraction_view, Claims.moderation_warn)
    async def infractions(self, ctx: commands.Context, user: t.Optional[discord.Member] = None):
        user = user or ctx.author
        repo = ModerationRepository()

        infractions = await repo.get_all_infractions_member(ctx.guild.id, user.id)
        chunked_infractions = self.chunk_list(infractions, 5)

        if len(infractions) == 0:
            embed = discord.Embed(color=Colors.ClemsonOrange)
            embed.title = 'Current Active Infractions'
            embed.set_author(name=self.get_full_name(user), icon_url=user.avatar_url)
            embed.add_field(name='Infractions', value='No Active Infractions')
            return await ctx.send(embed=embed)

        embeds = []
        for chunk in chunked_infractions:
            embed = discord.Embed(color=Colors.ClemsonOrange)
            embed.title = 'Current Active Infractions'
            embed.set_author(name=self.get_full_name(user), icon_url=user.avatar_url)

            for infraction in chunk:
                time = datetime.strptime(infraction.time, '%Y-%m-%d %H:%M:%S')
                embed.add_field(name=f'#{infraction.id} {infraction.iType.title()}  {INFRACTION_EMOJI_MAP[infraction.iType]}',
                                value=f'**Reason:** {infraction.reason}\n**Date:** {time.strftime("%m/%d/%Y")}',
                                inline=False)

            embeds.append(embed)

            # send the pages to the paginator service
        await self.bot.messenger.publish(Events.on_set_pageable_embed,
                                         pages=embeds,
                                         author=ctx.author,
                                         channel=ctx.channel,
                                         timeout=120)

    @infractions.command(aliases=['remove', 'clear', 'revoke'])
    @ext.long_help(
        'Removes an infraction from a user based on its unique Id, run the infractions command'
        'to see a list of infractions for a given user'
    )
    @ext.short_help('Removes an infraction')
    @ext.example(('infractions delete 1', 'infractions remove 2'))
    @ext.required_claims(Claims.moderation_warn)
    async def delete(self, ctx: commands.Context, infraction_id: int):
        repo = ModerationRepository()

        if not await repo.check_infraction(ctx.guild.id, infraction_id):
            embed = discord.Embed(color=Colors.Error)
            embed.title = 'Error: Infraction does not exist'
            embed.set_author(name=self.get_full_name(ctx.author), icon_url=ctx.author.avatar_url)
            return await ctx.send(embed=embed)

        await repo.delete_infractions(ctx.guild.id, infraction_id)

        embed = discord.Embed(color=Colors.ClemsonOrange)
        embed.title = f'Infractions {infraction_id} deleted successfully  :white_check_mark:'
        embed.set_author(name=self.get_full_name(ctx.author), icon_url=ctx.author.avatar_url)
        return await ctx.send(embed=embed)

    def get_full_name(self, author) -> str:
        return f'{author.name}#{author.discriminator}'

    def chunk_list(self, lst, n):
        """Yield successive n-sized chunks from lst."""
        for i in range(0, len(lst), n):
            yield lst[i:i + n]


def setup(bot):
    bot.add_cog(InfractionsCog(bot))
