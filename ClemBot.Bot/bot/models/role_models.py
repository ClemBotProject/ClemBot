from typing import Optional
from bot.utils.clem_bot_model import ClemBotModel


class Role(ClemBotModel):
    id: int
    name: Optional[str]
    is_assignable: bool


class RoleFull(Role):
    id: int
    name: Optional[str]
    guild_id: int
    admin: bool
    is_assignable: bool
