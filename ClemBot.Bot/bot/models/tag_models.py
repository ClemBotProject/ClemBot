from bot.utils.clem_bot_model import ClemBotModel

class Tag(ClemBotModel):
    name: str
    content: str
    creation_date: str
    guild_id: int
    user_id: int
    use_count: int = 0
