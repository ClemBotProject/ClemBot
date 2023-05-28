from enum import Enum, auto
from typing import Union

import discord

from bot.models.clem_bot_model import ClemBotModel


class EmoteBoard(ClemBotModel):
    guild_id: int
    name: str
    emote: str
    reaction_threshold: int
    allow_bot_posts: bool
    channels: list[int]


class EmoteBoardPost(ClemBotModel):
    user_id: int
    message_id: int
    channel_id: int
    reactions: list[int]

    def count_reaction(self, user: Union[int, discord.User, discord.Member]) -> bool:
        user_id = user if isinstance(user, int) else user.id
        return user_id != self.user_id and user_id not in self.reactions

    def as_link(self, guild: Union[int, discord.Guild]) -> str:
        guild_id = guild if isinstance(guild, int) else guild.id
        return f"https://discord.com/channels/{guild_id}/{self.channel_id}/{self.message_id}"


class EmoteBoardReactDto(ClemBotModel):
    update: bool
    reactions: int
    messages: dict[int, int]


class EmoteBoardLeaderboardType(Enum):

    total_reactions_received = auto()
    total_number_of_posts = auto()
    highest_number_of_reactions = auto()

