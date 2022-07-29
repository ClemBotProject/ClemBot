from bot.utils.clem_bot_model import ClemBotModel
from datetime import datetime


class Tag(ClemBotModel):
    name: str
    content: str
    creation_date: str
    guild_id: int
    user_id: int
    use_count: int = 0


class Infraction(ClemBotModel):
    id: int
    guild_id: int
    author_id: int
    subject_id: int
    type: str
    reason: str
    duration: int
    time: str
    active: int


class MessageDto(ClemBotModel):
    id: int
    content: str
    guild: int
    author: int
    channel: int
    time: datetime


class MessageEditDto(ClemBotModel):
    id: int
    content: str
    time: datetime
