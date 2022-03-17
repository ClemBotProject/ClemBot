import logging
import typing as t

import discord
import discord.ext.commands as commands

import bot.extensions as ext
from bot.consts import Claims, Colors, DesignatedChannels, Moderation
from bot.messaging.events import Events
from bot.utils.converters import Duration, DurationDelta
from bot.utils.user_choice import UserChoice

log = logging.getLogger(__name__)


class MuteCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @ext.command()
    @ext.long_help(
        'Mutes a user for a given amount of time with an optional reason'
    )
    @ext.short_help('Mutes a user')
    @ext.example(('mute @SomeUser 1d Timeout', 'mute @SomUser 2d1h5m A much longer timeout'))
    @ext.required_claims(Claims.moderation_mute)
    async def mute(self, ctx: commands.Context, subject: discord.Member, time: DurationDelta, *, reason: t.Optional[str]):

        duration_str = self._get_time_str(time)
        time = await Duration().convert(ctx, time)

        if ctx.author.top_role.position <= subject.top_role.position:
            embed = discord.Embed(color=Colors.Error)
            embed.title = f'Error: Invalid Permissions'
            embed.add_field(name='Reason', value='Cannot moderate someone with the same rank or higher')
            embed.set_author(name=self.get_full_name(ctx.author), icon_url=ctx.author.display_avatar.url)
            return await ctx.send(embed=embed)

        mute_role = discord.utils.get(ctx.guild.roles, name=Moderation.mute_role_name)
        if not mute_role:
            if not await self._create_mute_role(ctx):
                return

        #Publish that a mute happened
        await self.bot.messenger.publish(Events.on_bot_mute,
                                         guild=ctx.guild,
                                         author=ctx.author,
                                         subject=subject,
                                         duration=time,
                                         reason=reason)

        embed = discord.Embed(color=Colors.ClemsonOrange)
        embed.title = f'{self.get_full_name(subject)} Muted :mute:'
        embed.set_author(name=self.get_full_name(ctx.author), icon_url=ctx.author.display_avatar.url)
        embed.set_thumbnail(url=subject.display_avatar.url)
        embed.description = f'**{duration_str}** \n{reason}'

        await ctx.send(embed=embed)

        # Send the mute in the mod channels
        embed = discord.Embed(color=Colors.ClemsonOrange)
        embed.title = 'Guild Member Muted :mute:'
        embed.set_author(name=f'{self.get_full_name(ctx.author)}\nId: {ctx.author.id}', icon_url=ctx.author.display_avatar.url)
        embed.add_field(name=self.get_full_name(subject), value=f'Id: {subject.id}')
        embed.add_field(name='Duration :timer:', value=duration_str)
        embed.add_field(name='Reason :page_facing_up:', value=f'```{reason}```', inline=False)
        embed.add_field(name='Message Link  :rocket:', value=f'[Link]({ctx.message.jump_url})')
        embed.set_thumbnail(url=subject.display_avatar.url)

        await self.bot.messenger.publish(Events.on_send_in_designated_channel,
                                         DesignatedChannels.moderation_log,
                                         ctx.guild.id,
                                         embed)

        # Dm the user who was muted
        embed = discord.Embed(color=Colors.ClemsonOrange)
        embed.title = f'You have been muted  :mute:'
        embed.set_author(name=self.get_full_name(ctx.author), icon_url=ctx.author.display_avatar.url)
        embed.set_thumbnail(url=str(ctx.guild.icon.url))
        embed.add_field(name='Duration :timer:', value=duration_str)
        embed.add_field(name='Reason :page_facing_up:', value=f'```{reason}```', inline=False)
        embed.description = f'**Guild:** {ctx.guild.name}'

        try:
            await subject.send(embed=embed)
        except (discord.Forbidden, discord.HTTPException):
            embed = discord.Embed(color=Colors.ClemsonOrange)
            embed.title = f'Dm Mute to {self.get_full_name(subject)} forbidden'
            await self.bot.messenger.publish(Events.on_send_in_designated_channel,
                                             DesignatedChannels.moderation_log,
                                             ctx.guild.id,
                                             embed)


    @ext.command()
    @ext.long_help(
        'Unmutes a user for a with an optional reason'
    )
    @ext.short_help('Unmutes a user')
    @ext.example('Unmute @SomeUser Timeout')
    @ext.required_claims(Claims.moderation_mute)
    async def unmute(self, ctx: commands.Context, subject: discord.Member, *, reason: t.Optional[str]):
        mute_role = discord.utils.get(subject.guild.roles, name=Moderation.mute_role_name)

        if not mute_role:
            embed = discord.Embed(color=Colors.Error)
            embed.title = f'Error: Mute role not found'
            embed.add_field(name='Reason', value='Run the mute command to initiate mute role activation')
            embed.set_author(name=self.get_full_name(ctx.author), icon_url=ctx.author.display_avatar.url)
            return await ctx.send(embed=embed)

        mutes = await self.bot.moderation_route.get_guild_mutes_user(subject.guild.id, subject.id)
        mutes = [mute for mute in mutes if mute.active]

        if not mutes:
            embed = discord.Embed(color=Colors.Error)
            embed.title = f'Error: This user has no active mutes'
            embed.set_author(name=self.get_full_name(ctx.author), icon_url=ctx.author.display_avatar.url)
            return await ctx.send(embed=embed)

        for mute in mutes:
            await self.bot.messenger.publish(Events.on_bot_unmute,
                                             subject.guild.id,
                                             subject.id,
                                             mute.id,
                                             reason,
                                             ctx.author)

        embed = discord.Embed(color=Colors.ClemsonOrange)
        embed.title = f'{self.get_full_name(subject)} Unmuted  :speaker:'
        embed.set_author(name=self.get_full_name(ctx.author), icon_url=ctx.author.display_avatar.url)
        embed.add_field(name='Reason :page_facing_up:', value=f'```{reason}```', inline=False)
        embed.set_thumbnail(url=subject.display_avatar.url)

        await ctx.send(embed=embed)

    async def _create_mute_role(self, ctx) -> bool:
        get_input = UserChoice(ctx=ctx, timeout=30)
        choice = await get_input.send_confirmation(
            content='Error: ClemBots Mute role not found. Would you like me to create it?',
            is_error=True)
        if not choice:
            embed = discord.Embed(color=Colors.Error)
            embed.title = f'Error: Mute Role not found, Cancelling operation'
            embed.set_author(name=self.get_full_name(ctx.author), icon_url=ctx.author.display_avatar.url)
            return False

        mute_role = await ctx.guild.create_role(name=Moderation.mute_role_name)
        await mute_role.edit(position=ctx.guild.me.top_role.position - 1)
        msg = await ctx.send('Configuring ClemBot Mute role (This might take a minute)')
        for channel in ctx.guild.channels:
            try:
                await channel.set_permissions(mute_role,
                                              speak=False,
                                              connect=False,
                                              stream=False,
                                              send_messages=False,
                                              send_messages_in_threads=False,
                                              create_public_threads=False,
                                              create_private_threads=False,
                                              send_tts_messages=False,
                                              add_reactions=False)
            except:
                pass

        await msg.delete()
        embed = discord.Embed(color=Colors.ClemsonOrange)
        embed.title = f'@{Moderation.mute_role_name} Successfully Configured  :white_check_mark:'
        await ctx.send(embed=embed)
        return True

    def get_full_name(self, author) -> str:
        return f'{author.name}#{author.discriminator}'

    def _get_time_str(self, elapsed):
        s = ''
        if elapsed.days > 0:
            s += f'{elapsed.days} Day{"s" if elapsed.days > 1 else ""} '
        if elapsed.hours > 0:
            s += f'{elapsed.hours} Hour{"s" if elapsed.hours > 1 else ""}'
        if elapsed.minutes > 0:
            s += f'{elapsed.minutes} Minute{"s" if elapsed.minutes > 1 else ""}'
        return s


def setup(bot):
    bot.add_cog(MuteCog(bot))
