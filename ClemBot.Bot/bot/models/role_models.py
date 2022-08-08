from typing import Optional

from bot.models.clem_bot_model import ClemBotModel


class Role(ClemBotModel):
    id: int
    name: str
    is_assignable: bool


class RoleFull(Role):
    id: int
    name: str
    guild_id: int
    admin: bool
    is_assignable: bool
