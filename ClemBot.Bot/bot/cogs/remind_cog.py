import logging

import discord
import discord.ext.commands as commands

import bot.extensions as ext
from bot.clem_bot import ClemBot
from bot.consts import Colors
from bot.messaging.events import Events
from bot.models.reminder_models import Reminder
from bot.utils import converters
from bot.utils.helpers import format_duration

log = logging.getLogger(__name__)


class RemindCog(commands.Cog):
    def __init__(self, bot: ClemBot):
        self.bot = bot

    @ext.group(aliases=["remindme", "remind"], case_insensitive=True, invoke_without_command=True)
    @ext.long_help(
        """
        This command will direct message the user with their message at specified time in the future.

        This command supports many different time specifiers as listed below.
        Specifiers:
            - years: `Y`, `y`, `year`, `years`
            - months: `M`, `month`, `months`
            - weeks: `w`, `W`, `week`, `weeks`
            - days: `d`, `D`, `day`, `days`
            - hours: `H`, `h`, `hour`, `hours`
            - minutes: `m`, `min`, `minute`, `minutes`
            - seconds: `S`, `sec`, `s`, `second`, `seconds`

        """
    )
    @ext.short_help("Creates a reminder")
    @ext.example(
        (
            "reminder 24h",
            "reminder 5m Exam!",
            "reminder 1h Homework!",
            "reminder 4y Graduation",
            "reminder 3y1M4w1d5h9m2s Pi",
        )
    )
    async def reminder(
        self, ctx: ext.ClemBotCtx, wait: converters.FutureDuration, *, content: str | None
    ) -> None:
        try:
            await self.bot.messenger.publish(
                Events.on_set_reminder, ctx.author.id, ctx.message.jump_url, wait, content
            )
        except Exception as e:
            log.error("Failed to create reminder.", exc_info=e)
            return await self._error_embed(ctx, "Failed to create reminder.")
        embed = discord.Embed(title="⏰ Reminder Created", color=Colors.ClemsonOrange)
        embed.add_field(name="Time", value=format_duration(wait))
        embed.add_field(name="Message", value=f"{content or None}")
        embed.set_footer(text=str(ctx.author), icon_url=ctx.author.display_avatar.url)
        await ctx.send(embed=embed)

    @reminder.command(name="list")
    @ext.long_help("List all of your reminders that have not gone off.")
    @ext.short_help("List all of your reminders.")
    async def list_reminders(self, ctx: ext.ClemBotCtx) -> None:
        reminders = await self.bot.user_route.get_reminders(ctx.author.id)
        if len(reminders) == 0:
            embed = discord.Embed(
                title="⏰ Reminder",
                color=Colors.ClemsonOrange,
                description="You have no existing reminders.",
            )
            embed.set_footer(text=str(ctx.author), icon_url=ctx.author.display_avatar.url)
            await ctx.send(embed=embed)
            return

        reminder_pages = await self._reminder_pages(ctx, reminders)
        await self.bot.messenger.publish(
            Events.on_set_pageable_embed,
            pages=reminder_pages,
            author=ctx.author,
            channel=ctx.channel,
            timeout=360,
        )

    @reminder.command(aliases=["remove"])
    @ext.long_help("Delete a specific reminder.")
    @ext.short_help("Delete a reminder.")
    async def delete(self, ctx: ext.ClemBotCtx, reminder_id: int) -> None:
        reminder = await self.bot.reminder_route.get_reminder(reminder_id)
        if not reminder:
            return await self._error_embed(
                ctx, f"A reminder with the ID `{reminder_id}` does not exist."
            )
        if reminder.user_id != ctx.author.id:
            return await self._error_embed(ctx, "You do not own this reminder!")
        if reminder.dispatched:
            return await self._error_embed(
                ctx, f"The reminder with the ID `{reminder_id}` was already dispatched/deleted."
            )
        await self.bot.messenger.publish(Events.on_delete_reminder, reminder_id)
        embed = discord.Embed(title="⏰ Reminder Deleted", color=Colors.ClemsonOrange)
        embed.description = f"Successfully deleted reminder #{reminder_id}."
        embed.set_footer(text=str(ctx.author), icon_url=ctx.author.display_avatar.url)
        await ctx.send(embed=embed)

    async def _reminder_pages(
        self, ctx: ext.ClemBotCtx, reminders: list[Reminder]
    ) -> list[discord.Embed]:
        pages = []
        for reminder in reminders:
            embed = discord.Embed(title="⏰ Reminder", color=Colors.ClemsonOrange)
            embed.add_field(name="Reminder ID", value=reminder.id)
            embed.add_field(name="Original Message", value=f"[Link]({reminder.link})")
            embed.add_field(
                name="Alarm Time", value=reminder.time.strftime("%x at %X UTC"), inline=False
            )
            embed.add_field(name="Message", value=reminder.content)
            embed.set_footer(
                text=f'To delete this reminder, type "{await self.bot.current_prefix(ctx)}reminder delete {reminder.id}".'
            )
            pages.append(embed)
        return pages

    async def _error_embed(self, ctx: ext.ClemBotCtx, description: str) -> None:
        """Shorthand for sending an error message w/ consistent formatting."""
        embed = discord.Embed(title="Error", color=Colors.Error, description=description)
        embed.set_footer(text=str(ctx.author), icon_url=ctx.author.display_avatar.url)
        msg = await ctx.send(embed=embed)
        await self.bot.messenger.publish(
            Events.on_set_deletable, msg=msg, author=ctx.author, timeout=60
        )


async def setup(bot: ClemBot) -> None:
    await bot.add_cog(RemindCog(bot))
