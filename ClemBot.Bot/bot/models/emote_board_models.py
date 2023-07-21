from typing import Union

import discord

from bot.models.clem_bot_model import ClemBotModel


class EmoteBoard(ClemBotModel):
    name: str
    emote: str
    reaction_threshold: int = 4
    allow_bot_posts: bool = False
    channels: list[int]


class EmoteBoardPost(ClemBotModel):
    name: str
    channel_id: int
    message_id: int
    user_id: int
    reactions: list[int]
    channel_message_ids: dict[int, int]

    def count_reaction(self, user: Union[int, discord.User, discord.Member]) -> bool:
        user_id = user if isinstance(user, int) else user.id
        return user_id != self.user_id and user_id not in self.reactions

    def as_link(self, guild: Union[int, discord.Guild]) -> str:
        guild_id = guild if isinstance(guild, int) else guild.id
        return f"https://discord.com/channels/{guild_id}/{self.channel_id}/{self.message_id}"


class EmoteBoardReaction(ClemBotModel):
    update: bool
    reactions: int | None


class PopularLeaderboardSlot(ClemBotModel):
    user_id: int
    channel_id: int
    message_id: int
    reaction_count: int
    emote: str

    def as_link(self, guild: Union[int, discord.Guild]) -> str:
        guild_id = guild if isinstance(guild, int) else guild.id
        return f"https://discord.com/channels/{guild_id}/{self.channel_id}/{self.message_id}"

    def format(self, index: int, guild: Union[int, discord.Guild]) -> str:
        link = self.as_link(guild)
        return (
            f"{index + 1}. **<@{self.user_id}> {self.emote} {self.reaction_count} [Link]({link})**"
        )


class PostLeaderboardSlot(ClemBotModel):
    user_id: int
    post_count: int

    def format(self, index: int, board_name: str | None = None) -> str:
        return f"{index + 1}. **<@{self.user_id}> {self.post_count}{f' {board_name}' if board_name else ''} posts**"


class ReactionLeaderboardSlot(ClemBotModel):
    user_id: int
    reaction_count: int

    def format(self, index: int, emote: Union[str, discord.Emoji, None] = None) -> str:
        if isinstance(emote, discord.Emoji):
            emote = str(emote)
        return f"{index + 1}. **<@{self.user_id}> {self.reaction_count}{f' {emote}' if emote else ''} reactions**"
