from bot.models.clem_bot_model import ClemBotModel


class Tag(ClemBotModel):
    name: str
    content: str
    creation_date: str
    guild_id: int
    user_id: int
    use_count: int = 0


class TagDelete(ClemBotModel):
    id: int
    name: str | None
    content: str | None


class TagInvoke(ClemBotModel):
    guildId: int
    name: str | None
