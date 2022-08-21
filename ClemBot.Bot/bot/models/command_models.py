from bot.models.clem_bot_model import ClemBotModel


class CommandModel(ClemBotModel):

    command_name: str
    disabled: bool
    guild_id: int
    channel_ids: list[int]
