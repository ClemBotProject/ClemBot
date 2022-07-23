import logging
from datetime import datetime

import discord
import discord.ext.commands as commands

from typing import Optional
from bot.models import Reminder
from bot.clem_bot import ClemBot
from bot.consts import Colors
from bot.messaging.events import Events
from bot.services.base_service import BaseService
from bot.utils import converters

log = logging.getLogger(__name__)

# todo: dataclasses and reminder_route


class ReminderService(BaseService):

    def __init__(self, *, bot: ClemBot):
        super().__init__(bot)

    async def reminder_callback(self, reminder_id: int):
        reminder = await self.bot.reminder_route.get_reminder(reminder_id, raise_on_error=True)
        if not reminder:
            return  # todo: raise error?
        user = self.bot.get_user(reminder.user_id)
        embed = discord.Embed(title='⏰ Reminder', color=Colors.ClemsonOrange,
                              description=f'This is your reminder to **{reminder.content}**!')
        embed.add_field(name='Original Message', value=f'[Link]({reminder.link})')
        await self.bot.reminder_route.dispatch_reminder(reminder_id, raise_on_error=True)
        await user.send(embed=embed)

    @BaseService.Listener(Events.on_set_reminder)
    async def on_set_reminder(self, ctx: commands.Context, time: datetime, content: Optional[str]):
        reminder_id = await self.bot.reminder_route.create_reminder(ctx.author.id,
                                                                    time,
                                                                    ctx.message.id,
                                                                    ctx.message.jump_url,
                                                                    content,
                                                                    raise_on_error=True)
        task_id = self.bot.scheduler.schedule_at(self.reminder_callback(reminder_id), time=time)
        await self.bot.reminder_route.update_reminders({reminder_id: task_id}, raise_on_error=True)
        # self.bot.reminder_route.update_reminder(reminder_id, task_id, raise_on_error=True)

    @BaseService.Listener(Events.on_delete_reminder)
    async def on_delete_reminder(self, reminder_id: int):
        return await self.bot.reminder_route.dispatch_reminder(reminder_id, raise_on_error=True)


# class RemindService(BaseService):
#     def __init__(self, *, bot):
#         super().__init__(bot)
#
#     @BaseService.Listener(Events.on_set_reminder)
#     async def on_set_reminder(self, userId: int, wait: converters.Duration, messageId: int, link: str):
#         await RemindRepository().insert_reminder(userId, messageId, link, wait)
#         self.bot.scheduler.schedule_at(self.reminder_callback(userId, messageId), time=wait)
#
#     async def reminder_callback(self, userId: int, messageId: int):
#
#         data = await RemindRepository().query_reminder(userId, messageId)
#
#         user: discord.User = self.bot.get_user(data['fk_userId'])
#
#         message = await MessageRepository().get_message(data['fk_messageId'])
#
#         time = message['time'].split('.')[0]
#         message = message['content'].split(' ', 2)
#
#         if len(message) < 3:
#             message = 'None'
#         else:
#             message = message[2]
#
#         embed = discord.Embed(title='⏰Reminder', color = Colors.ClemsonOrange)
#         embed.add_field(name='Message', value = message, inline= False)
#         embed.add_field(name='Message Date', value = time)
#         embed.add_field(name='Message Link', value = "[message link](" + data['link'] + ")", inline=False)
#         await user.send(embed = embed)
#
#         await RemindRepository().delete_reminder(data['id'])
#
#     async def load_service(self):
#         reminders = await RemindRepository().get_all_reminders()
#         for reminder in reminders:
#             wait: datetime = datetime.strptime(reminder['time'], '%Y-%m-%d %H:%M:%S.%f')
#             if (wait - datetime.utcnow()).total_seconds() <= 0:
#                 await self.reminder_callback(reminder['fk_userId'], reminder['fk_messageId'])
#             else:
#                 self.bot.scheduler.schedule_at(self.reminder_callback(reminder['fk_userId'], reminder['fk_messageId']), time=wait)
