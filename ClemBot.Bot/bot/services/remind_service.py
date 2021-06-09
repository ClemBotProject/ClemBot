import logging
from datetime import datetime

import discord

from bot.consts import Colors
from bot.messaging.events import Events
from bot.services.base_service import BaseService
from bot.utils import converters

log = logging.getLogger(__name__)


"""
class RemindService(BaseService):
    def __init__(self, *, bot):
        super().__init__(bot)
        
    @BaseService.Listener(Events.on_set_reminder)
    async def on_set_reminder(self, userId: int, wait: converters.Duration, messageId: int, link: str):
        await RemindRepository().insert_reminder(userId, messageId, link, wait)
        self.bot.scheduler.schedule_at(self.reminder_callback(userId, messageId), time=wait)

    async def reminder_callback(self, userId: int, messageId: int):     

        data = await RemindRepository().query_reminder(userId, messageId)
        
        user: discord.User = self.bot.get_user(data['fk_userId'])

        message = await MessageRepository().get_message(data['fk_messageId'])
        
        time = message['time'].split('.')[0]
        message = message['content'].split(' ', 2)
        
        if len(message) < 3:
            message = 'None'
        else:
            message = message[2]
        
        embed = discord.Embed(title='⏰Reminder', color = Colors.ClemsonOrange)
        embed.add_field(name='Message', value = message, inline= False)
        embed.add_field(name='Message Date', value = time)
        embed.add_field(name='Message Link', value = "[message link](" + data['link'] + ")", inline=False)
        await user.send(embed = embed)
        
        await RemindRepository().delete_reminder(data['id'])

    async def load_service(self):
        reminders = await RemindRepository().get_all_reminders()
        for reminder in reminders:
            wait: datetime = datetime.strptime(reminder['time'], '%Y-%m-%d %H:%M:%S.%f')
            if (wait - datetime.utcnow()).total_seconds() <= 0:
                await self.reminder_callback(reminder['fk_userId'], reminder['fk_messageId'])
            else:
                self.bot.scheduler.schedule_at(self.reminder_callback(reminder['fk_userId'], reminder['fk_messageId']), time=wait)
"""