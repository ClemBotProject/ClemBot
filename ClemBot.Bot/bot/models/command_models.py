from bot.models.clem_bot_model import ClemBotModel


class BlackListCommandModel(ClemBotModel):
    channel_id: int
    silently_fail: bool


class CommandModel(ClemBotModel):
    command_name: str
    guild_disabled: bool
    guild_id: int
    white_listed_channel_ids: list[int]
    black_listed_channel_ids: list[BlackListCommandModel]


class CommandStatusModel(ClemBotModel):

    disabled: bool
    silently_fail: bool | None
