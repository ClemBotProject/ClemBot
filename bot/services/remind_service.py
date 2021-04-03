from bot.data.message_repository import MessageRepository
from datetime import datetime
from uuid import uuid4
import logging

import discord

from bot.consts import Colors
from bot.utils import converters
from bot.messaging.events import Events
from bot.services.base_service import BaseService
from bot.data.remind_repository import RemindRepository

log = logging.getLogger(__name__)


class RemindService(BaseService):
    def __init__(self, *, bot):
        super().__init__(bot)
        
    @BaseService.Listener(Events.on_set_reminder)
    async def on_set_reminder(self, userId: int, wait: converters.Duration, message: str, link: str):
        id = str(uuid4())
        await RemindRepository().insert_reminder(id, userId, message, link, wait)
        self.bot.scheduler.schedule_at(self.reminder_callback(id), time=wait)

    async def reminder_callback(self, id: str):       
        data = await RemindRepository().get_reminder(id)
        
        user: discord.User = self.bot.get_user(data['fk_userId'])

        message = await MessageRepository().get_message(data['fk_messageId'])
        
        message = message['content'].split(' ', 2)
        if len(message) < 3:
            message = 'None'
        else:
            message = message[2]
        
        embed = discord.Embed(title='⏰Reminder', color = Colors.ClemsonOrange)
        embed.add_field(name='Message', value = message, inline= False)
        embed.add_field(name='Message Link', value = data['link'], inline=False)
        await user.send(embed = embed)
        
        await RemindRepository().delete_reminder(id)

    async def load_service(self):
        reminders = await RemindRepository().get_all_reminders()
        for reminder in reminders:
            wait: datetime = datetime.strptime(reminder['time'], '%Y-%m-%d %H:%M:%S.%f')
            if (wait - datetime.utcnow()).total_seconds() <= 0:
                await self.reminder_callback(reminder['id'])
            else:
                self.bot.scheduler.schedule_at(self.reminder_callback(reminder['id']), time=wait)