from enum import Enum, auto
from typing import Union

import discord

from bot.clem_bot import ClemBot
from bot.models.clem_bot_model import ClemBotModel


class EmoteBoard(ClemBotModel):
    guild_id: int
    name: str
    emote: str
    reaction_threshold: int = 4
    allow_bot_posts: bool = False
    channels: list[int]


class EmoteBoardPost(ClemBotModel):
    user_id: int
    message_id: int
    channel_id: int
    board_name: str
    reactions: list[int]

    def count_reaction(self, user: Union[int, discord.User, discord.Member]) -> bool:
        user_id = user if isinstance(user, int) else user.id
        return user_id != self.user_id and user_id not in self.reactions

    def as_link(self, guild: Union[int, discord.Guild]) -> str:
        guild_id = guild if isinstance(guild, int) else guild.id
        return f"https://discord.com/channels/{guild_id}/{self.channel_id}/{self.message_id}"


class EmoteBoardReaction(ClemBotModel):
    update: bool
    reactions: int | None
    messages: dict[int, int] | None


class PopularLeaderboardSlot(ClemBotModel):
    user_id: int
    channel_id: int
    message_id: int
    reaction_count: int
    emote: str

    def as_link(self, guild: Union[int, discord.Guild]) -> str:
        guild_id = guild if isinstance(guild, int) else guild.id
        return f"https://discord.com/channels/{guild_id}/{self.channel_id}/{self.message_id}"

    def format(self, index: int, guild_id: int) -> str:
        link = self.as_link(guild_id)
        return f"**{index + 1}. <@{self.user_id}> - {self.emote} {self.reaction_count} - [Link]({link})**"
