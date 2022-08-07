from typing import Optional
from bot.models.clem_bot_model import ClemBotModel


class User(ClemBotModel):
    id: int
    name: Optional[str]
    guilds: list[int]
