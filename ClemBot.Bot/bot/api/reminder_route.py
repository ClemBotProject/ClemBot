import datetime
import typing as t

from bot.models import Reminder
from bot.api.api_client import ApiClient
from bot.api.base_route import BaseRoute


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

        resp = await self._client.post('reminders', data=json, **kwargs)

        if not resp:
            return None

        return resp['Id']

    async def dispatch_reminder(self, reminder_id: int, **kwargs):
        return await self._client.patch(f'reminders/{reminder_id}/dispatch', **kwargs)


