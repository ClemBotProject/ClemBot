from typing import Optional

from bot.models.clem_bot_model import ClemBotModel


class Channel(ClemBotModel):
    id: int
    name: Optional[str]
    guild_id: int
