from bot.models.clem_bot_model import ClemBotModel


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
