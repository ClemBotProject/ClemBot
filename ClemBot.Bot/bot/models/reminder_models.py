from typing import Optional
from bot.models.clem_bot_model import ClemBotModel

class Reminder(ClemBotModel):
    id: int
    link: str
    content: Optional[str]
    time: str
    dispatched: bool
    user_id: int
