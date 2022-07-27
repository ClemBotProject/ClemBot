from bot.utils.clem_bot_model import ClemBotModel


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
