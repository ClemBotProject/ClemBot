import logging
import typing as t
import uuid
from datetime import datetime

import discord
import discord.ext.commands as commands

from bot.clem_bot import ClemBot
from bot.consts import Colors
from bot.messaging.events import Events
from bot.services.base_service import BaseService

log = logging.getLogger(__name__)


class ReminderService(BaseService):

    def __init__(self, *, bot: ClemBot):
        super().__init__(bot)
        self.reminders: t.Dict[int, uuid.UUID] = {}

    async def _reminder_callback(self, reminder_id: int):
        reminder = await self.bot.reminder_route.get_reminder(reminder_id, raise_on_error=True)
        if not reminder:
            log.warning(f'Reminder with id {reminder_id} returned None from API call.')
            return
        user = self.bot.get_user(reminder.user_id)
        embed = discord.Embed(title='⏰ Reminder', color=Colors.ClemsonOrange,
                              description="Time's up!")
        embed.add_field(name='Original Message', value=f'[Link]({reminder.link})')
        embed.add_field(name='Message', value=reminder.content)
        embed.set_footer(text=str(user), icon_url=user.display_avatar.url)
        await self.bot.reminder_route.dispatch_reminder(reminder_id, raise_on_error=True)
        await user.send(embed=embed)

    @BaseService.Listener(Events.on_set_reminder)
    async def on_set_reminder(self, ctx: commands.Context, time: datetime, content: t.Optional[str]):
        reminder_id = await self.bot.reminder_route.create_reminder(ctx.author.id,
                                                                    time,
                                                                    ctx.message.jump_url,
                                                                    content,
                                                                    raise_on_error=True)
        task_id = self.bot.scheduler.schedule_at(self._reminder_callback(reminder_id), time=time)
        self.reminders[reminder_id] = task_id

    @BaseService.Listener(Events.on_delete_reminder)
    async def on_delete_reminder(self, reminder_id: int):
        reminder_id = await self.bot.reminder_route.dispatch_reminder(reminder_id, raise_on_error=True)
        self.bot.scheduler.cancel(self.reminders[reminder_id])
        self.reminders.pop(reminder_id)

    async def load_service(self):
        reminders = await self.bot.reminder_route.fetch_all_reminders(raise_on_error=True)
        for (reminder_id, time) in reminders:
            if (time - datetime.utcnow()).total_seconds() <= 0:
                await self._reminder_callback(reminder_id)
                await self.bot.reminder_route.dispatch_reminder(reminder_id)
                continue

            task_id = self.bot.scheduler.schedule_at(self._reminder_callback(reminder_id), time=time)
            self.reminders[reminder_id] = task_id
