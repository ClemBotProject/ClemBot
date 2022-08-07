from typing import Optional
from bot.models.clem_bot_model import ClemBotModel


class Guild(ClemBotModel):
    id: int
    name: Optional[str]
    welcome_message: Optional[str]


class SlotScore(ClemBotModel):
    high_score: int
    user_id: int
