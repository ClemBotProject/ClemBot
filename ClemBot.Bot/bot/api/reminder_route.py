import datetime

from typing import Optional
from bot.api.api_client import ApiClient
from bot.api.base_route import BaseRoute


class ReminderRoute(BaseRoute):

    def __init__(self, api_client: ApiClient):
        super().__init__(api_client)

    def create_reminder(self,
                        user_id: int,
                        time: datetime,
                        message_id: int,
                        message_url: str,
                        content: Optional[str],
                        **kwargs) -> Optional[int]:
        json = {
            'UserId': user_id,
            'Time': time,
            'MessageId': message_id,
            'Link': message_url,
            'Content': content
        }

        resp = await self._client.post('bot/reminders', data=json, **kwargs)

        if not resp:
            return None

        return resp['Id']

