from bot.models.clem_bot_model import ClemBotModel
from datetime import datetime


class SingleBatchMessage(ClemBotModel):
    id: int
    content: str
    guild: int
    author: int
    channel: int
    time: datetime


class SingleBatchMessageEdit(ClemBotModel):
    id: int
    content: str
    time: datetime


class Message(ClemBotModel):
    id: int
    content: str
    guild_id: int
    channel_id: int
    user_id: int
