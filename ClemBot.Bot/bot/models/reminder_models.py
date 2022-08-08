from datetime import datetime

from bot.models.clem_bot_model import ClemBotModel


class Reminder(ClemBotModel):
    id: int
    link: str
    content: str | None
    time: datetime
    dispatched: bool
    user_id: int


class ReminderReload(ClemBotModel):
    id: int
    time: datetime
