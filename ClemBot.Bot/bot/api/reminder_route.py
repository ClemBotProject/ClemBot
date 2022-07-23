import typing as t
import uuid

from datetime import datetime
from bot.models import Reminder
from bot.api.api_client import ApiClient
from bot.api.base_route import BaseRoute
from bot.utils.helpers import parse_datetime


class ReminderRoute(BaseRoute):

    def __init__(self, api_client: ApiClient):
        super().__init__(api_client)

    async def create_reminder(self,
                              user_id: int,
                              time: datetime,
                              message_id: int,
                              message_url: str,
                              content: t.Optional[str],
                              **kwargs) -> t.Optional[int]:
        json = {
            'UserId': user_id,
            'Time': time,
            'MessageId': message_id,
            'Link': message_url,
            'Content': content
        }

        resp = await self._client.post('bot/reminders/create', data=json, **kwargs)

        if not resp:
            return None

        return resp['Id']

    async def dispatch_reminder(self, reminder_id: int, **kwargs) -> t.Optional[uuid.UUID]:
        """
            Tells the API to mark the reminder with the given reminder_id as dispatched.
            Returns: the task uuid stored in the DB
        """
        return await self._client.patch(f'bot/reminders/{reminder_id}/dispatch', **kwargs)

    async def get_reminder(self, reminder_id: int, **kwargs) -> t.Optional[Reminder]:
        resp = await self._client.get(f'bot/reminders/{reminder_id}/details', **kwargs)

        if not resp:
            return None

        return Reminder.from_dict(resp)

    async def fetch_all_reminders(self, **kwargs) -> t.List[t.Tuple[int, datetime]]:
        resp = await self._client.get('bot/reminders', **kwargs)

        if not resp:
            return []

        return [(i['Id'], parse_datetime(i['Time'])) for i in resp]

    async def update_reminders(self, reminders: t.Dict[int, uuid.UUID], **kwargs):
        json = {
            'ReminderTaskIds': reminders
        }
        await self._client.patch('bot/reminders/edit', data=json, **kwargs)
