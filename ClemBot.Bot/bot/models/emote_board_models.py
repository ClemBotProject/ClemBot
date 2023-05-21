from typing import Union

import discord

from bot.models.clem_bot_model import ClemBotModel


class EmoteBoard(ClemBotModel):
    guild_id: int
    name: str
    emote: str
    reaction_threshold: int
    allow_bot_posts: bool


class EmoteBoardPost(ClemBotModel):
    user_id: int
    message_id: int
    board_message_id: int
    emote_board_id: int
    reactions: list[int]

    def count_reaction(self, user: Union[int, discord.User, discord.Member]) -> bool:
        user_id = user if isinstance(user, int) else user.id
        return user_id != self.user_id and user_id not in self.reactions
