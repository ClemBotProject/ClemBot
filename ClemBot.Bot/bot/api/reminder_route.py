import typing as t

from datetime import datetime
from bot.models.reminder_models import Reminder, ReminderReload
from bot.api.api_client import ApiClient
from bot.api.base_route import BaseRoute
from bot.utils.helpers import parse_datetime, format_datetime


class ReminderRoute(BaseRoute):

    def __init__(self, api_client: ApiClient):
        super().__init__(api_client)

    async def create_reminder(self,
                              user_id: int,
                              time: datetime,
                              message_url: str,
                              content: str | None,
                              **kwargs: t.Any) -> int | None:
        json = {
            'UserId': user_id,
            'Time': format_datetime(time),
            'Link': message_url,
            'Content': content
        }

        resp = await self._client.post('bot/reminders/create', data=json, **kwargs)

        if not resp:
            return None

        return t.cast(int, resp['id'])

    async def dispatch_reminder(self, reminder_id: int, **kwargs: t.Any) -> int | None:
        """
            Tells the API to mark the reminder with the given reminder_id as dispatched.
            Returns: the reminder id stored in the DB
        """

        return t.cast(int | None, await self._client.patch(f'bot/reminders/{reminder_id}/dispatch', **kwargs))

    async def get_reminder(self, reminder_id: int, **kwargs: t.Any) -> Reminder | None:
        resp = await self._client.get(f'bot/reminders/{reminder_id}/details', **kwargs)

        if not resp:
            return None

        return Reminder(**resp)

    async def fetch_all_reminders(self, **kwargs: t.Any) -> list[ReminderReload]:
        resp = await self._client.get('bot/reminders', **kwargs)

        if not resp:
            return []

        return [ReminderReload(**i) for i in resp]
