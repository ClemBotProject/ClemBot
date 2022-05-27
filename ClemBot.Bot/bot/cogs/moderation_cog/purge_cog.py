import logging
import uuid
import os

import discord
import discord.ext.commands as commands
import bot.extensions as ext
import typing as t

from datetime import datetime
from bot.consts import Claims, Colors, DesignatedChannels
from bot.utils.converters import Duration, DurationDelta
from bot.messaging.events import Events

log = logging.getLogger(__name__)

MAX_REASON_LENGTH = 1015  # 1024 - 9 (for "```REASON...```")
ASSETS_FOLDER = 'bot/cogs/moderation_cog/assets/'


class PurgeCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @ext.command()
    @ext.required_claims(Claims.moderation_purge)
    @ext.short_help('Purges up to 7 days of messages.')
    @ext.long_help('Purge up to 7 days of messages from a given user.')
    @ext.example(['purge @User 10m NSFW', 'purge @User 7d Cleanup'])
    async def purge(self, ctx: commands.Context, subject: discord.Member, time: DurationDelta, *, reason: t.Optional[str] = None):
        duration_str = self._get_time_str(time)
        time = await Duration().subtract(ctx, time)
        # invalid role
        if ctx.author.top_role.position <= subject.top_role.position:
            return await self._error_embed(ctx, 'Invalid Permissions',
                                           desc='Cannot moderate someone with same rank or higher.')
        # send an embed saying we're processing
        msg = await self._processing_embed(ctx, subject, duration_str)
        # start purging
        deleted_messages = await ctx.channel.purge(limit=None, check=lambda m: m.author == subject, after=time)
        if len(deleted_messages) == 0:
            await msg.delete()
            return await self._error_embed(ctx, desc='No messages to purge within the timeframe.')

        # create the log
        file_path = self._create_log(ctx, subject, reason, time, deleted_messages)
        # create the embed to send to the mod log channel
        sent_reason = reason if len(reason) <= MAX_REASON_LENGTH else reason[0:MAX_REASON_LENGTH] + '...'

        embed = discord.Embed(title='Guild Member Purged :speech_balloon:', color=Colors.ClemsonOrange)
        embed.set_author(name=self.get_full_name(ctx.author), icon_url=ctx.author.display_avatar.url)
        embed.add_field(name=self.get_full_name(subject), value=f'Id: {subject.id}')
        embed.add_field(name='Duration :timer:', value=duration_str)
        embed.add_field(name='Reason :page_facing_up:', value=f'```{sent_reason}```', inline=False)
        embed.add_field(name='Message Link  :rocket:', value=f'[Link]({ctx.message.jump_url})')
        embed.set_thumbnail(url=subject.display_avatar.url)
        attachment = discord.File(fp=file_path)
        await self.bot.messenger.publish(Events.on_send_in_designated_channel,
                                         DesignatedChannels.moderation_log,
                                         ctx.guild.id,
                                         embed)
        # cleanup the log, delete old message, and send report
        self._cleanup_log(file_path)
        await msg.delete()
        await self._finished_embed(ctx, subject, len(deleted_messages), duration_str)

    def _cleanup_log(self, file_path: str):
        try:
            os.remove(file_path)
        except OSError:
            log.error(f'Failed to delete {file_path}.')

    def _create_log(self, ctx, subject: discord.Member, reason: str, time: datetime, messages) -> str:
        temp_file = ASSETS_FOLDER + str(uuid.uuid4()) + '.txt'
        with open(temp_file, 'w', encoding='utf8') as f:
            f.write('-------------------------- PURGE LOG --------------------------\n')
            f.write(f'Subject: {self.get_full_name(subject)} (ID: {subject.id})\n')
            f.write(f'Purged by: {self.get_full_name(ctx.author)} (ID: {ctx.author.id})\n')
            f.write(f'Reason: {reason}\n')
            f.write(f'Date & Time: {time.date()} at {time.timetz()}\n')
            f.write(f'Messages purged: {len(messages)}\n\n')
            f.write('-------------------------- BEGIN LOG --------------------------\n')
            for msg in messages:
                f.write(f'[{msg.created_at}] {msg.content}\n')
            f.write('-------------------------- END - LOG --------------------------\n')
            f.close()
        return temp_file

    async def _finished_embed(self, ctx, subject: discord.Member, message_count, duration) -> discord.Message:
        embed = discord.Embed(title=':eye_in_speech_bubble: Messages Purged', color=Colors.ClemsonOrange)
        embed.add_field(name='User', value=subject.mention)
        embed.add_field(name='Messages Purged', value=message_count)
        embed.add_field(name='Duration', value=duration)
        embed.set_footer(text=f'{ctx.author.name}#{ctx.author.discriminator}', icon_url=ctx.author.display_avatar.url)
        return await ctx.send(embed=embed)

    async def _processing_embed(self, ctx, subject: discord.Member, duration: str) -> discord.Message:
        """Shorthand for sending an embed saying the image is being generated"""
        embed = discord.Embed(title=':hourglass_flowing_sand: Purging Messages', color=Colors.ClemsonOrange,
                              description=f"Purging **{duration}** of {subject.mention}'s messages.\n\n"
                                          '_This may take several minutes..._')
        embed.set_footer(text=f'{ctx.author.name}#{ctx.author.discriminator}', icon_url=ctx.author.display_avatar.url)
        return await ctx.send(embed=embed)

    async def _error_embed(self, ctx, err: t.Optional[str] = None, *, desc: str):
        """Shorthand for sending an error message w/ consistent formatting."""
        embed = discord.Embed(title=f'Error{": " + err if err else ""}', color=Colors.Error, description=desc)
        embed.set_footer(text=self.get_full_name(ctx.author), icon_url=ctx.author.display_avatar.url)
        msg = await ctx.send(embed=embed)
        await self.bot.messenger.publish(Events.on_set_deletable, msg=msg, author=ctx.author, timeout=60)

    def get_full_name(self, author) -> str:
        return f'{author.name}#{author.discriminator}'

    def _get_time_str(self, elapsed):
        s = ''
        if elapsed.days > 0:
            s += f'{elapsed.days} Day{"s" if elapsed.days > 1 else ""} '
        if elapsed.hours > 0:
            s += f'{elapsed.hours} Hour{"s" if elapsed.hours > 1 else ""} '
        if elapsed.minutes > 0:
            s += f'{elapsed.minutes} Minute{"s" if elapsed.minutes > 1 else ""}'
        return s


def setup(bot):
    bot.add_cog(PurgeCog(bot))
