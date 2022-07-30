from bot.utils.clem_bot_model import ClemBotModel
from datetime import datetime


class Message(ClemBotModel):
    id: int
    content: str
    guild: int
    author: int
    channel: int
    time: datetime


class MessageEdit(ClemBotModel):
    id: int
    content: str
    time: datetime
