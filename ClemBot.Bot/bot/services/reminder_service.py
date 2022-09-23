import uuid
from datetime import datetime

import discord

from bot.clem_bot import ClemBot
from bot.consts import Colors
from bot.errors import ReminderError
from bot.messaging.events import Events
from bot.services.base_service import BaseService
from bot.utils.logging_utils import get_logger

log = get_logger(__name__)


class ReminderService(BaseService):
    def __init__(self, *, bot: ClemBot):
        super().__init__(bot)
        self.reminders: dict[int, uuid.UUID] = {}

    async def _reminder_callback(self, reminder_id: int) -> None:
        reminder = await self.bot.reminder_route.get_reminder(reminder_id, raise_on_error=True)
        if not reminder:
            log.warning(
                "Reminder with id {reminder_id} returned None from API call.",
                reminder_id=reminder_id,
            )
            return None
        user = self.bot.get_user(reminder.user_id)

        if not user:
            log.error("Unable to find remind user target: {id}", id=reminder.user_id)
            # Dispatch the reminder in the db anyway, if we cant find the user they probably left all of clembots servers
            await self.bot.reminder_route.dispatch_reminder(reminder_id, raise_on_error=True)
            return None

        embed = discord.Embed(
            title="⏰ Reminder", color=Colors.ClemsonOrange, description="Time's up!"
        )
        embed.add_field(name="Original Message", value=f"[Link]({reminder.link})")
        embed.add_field(name="Message", value=reminder.content)
        embed.set_footer(text=str(user), icon_url=user.display_avatar.url)
        await self.bot.reminder_route.dispatch_reminder(reminder_id, raise_on_error=True)
        await user.send(embed=embed)

    @BaseService.listener(Events.on_set_reminder)
    async def on_set_reminder(
        self, author_id: int, jump_url: str, time: datetime, content: str | None
    ) -> None:
        reminder_id = await self.bot.reminder_route.create_reminder(
            author_id, time, jump_url, content, raise_on_error=True
        )

        if not reminder_id:
            raise ReminderError("Creating reminder failed")

        task_id = self.bot.scheduler.schedule_at(self._reminder_callback(reminder_id), time=time)
        self.reminders[reminder_id] = task_id

    @BaseService.listener(Events.on_delete_reminder)
    async def on_delete_reminder(self, reminder_id: int) -> None:
        del_id = await self.bot.reminder_route.dispatch_reminder(reminder_id, raise_on_error=True)

        if not del_id:
            log.warning("Attempted to delete nonexistent reminder: {id}", id=reminder_id)
            return None

        self.bot.scheduler.cancel(self.reminders[reminder_id])
        self.reminders.pop(reminder_id)

    async def load_service(self) -> None:
        reminders = await self.bot.reminder_route.fetch_all_reminders(raise_on_error=True)
        for reminder in reminders:
            if (reminder.time - datetime.utcnow()).total_seconds() <= 0:
                await self._reminder_callback(reminder.id)
                await self.bot.reminder_route.dispatch_reminder(reminder.id)
                continue

            task_id = self.bot.scheduler.schedule_at(
                self._reminder_callback(reminder.id), time=reminder.time
            )
            self.reminders[reminder.id] = task_id
