from typing import Optional
from bot.models.clem_bot_model import ClemBotModel


class Thread(ClemBotModel):
    id: int
    name: Optional[str]
    guild_id: int
