import asyncio
import dataclasses
import typing as t

import discord

from bot.clem_bot import ClemBot
from bot.consts import Claims
from bot.messaging.events import Events
from bot.services.base_service import BaseService
from bot.utils.logging_utils import get_logger

log = get_logger(__name__)


@dataclasses.dataclass
class DeletableMessage:
    message_to_delete: list[discord.Message]
    author: int | None
    roles: list[discord.Role]


class DeleteMessageService(BaseService):
    """
    This service allows for messages sent by the bot to be deleted
    The messages by default are allowed by deleted by admins and the person who called the bot
    """

    def __init__(self, *, bot: ClemBot):
        super().__init__(bot)
        self.messages: dict[int, DeletableMessage] = {}

    # Called When a cog would like to be able to delete a message or messages
    @BaseService.listener(Events.on_set_deletable)
    async def set_message_deletable(
        self,
        *,
        msg: discord.Message | list[discord.Message],
        roles: discord.Role | list[discord.Role] | None = None,
        author: discord.Member | None = None,
        timeout: int | None = None
    ) -> None:

        msg_to_delete = [msg] if not isinstance(msg, list) else msg

        if roles is None:
            roles = []
        if not isinstance(roles, list):
            roles = [roles]

        self.messages[msg_to_delete[-1].id] = DeletableMessage(
            message_to_delete=msg_to_delete, roles=roles, author=author.id if author else None
        )

        # the emoji is placed on the last message in the list
        await msg_to_delete[-1].add_reaction("🗑️")

        async def message_delete_timeout() -> None:
            try:
                await msg_to_delete[-1].clear_reaction("🗑️")
                del self.messages[msg_to_delete[-1].id]
            except:
                pass
            finally:
                log.info("Message: {message} timed out as deletable", message=msg_to_delete[-1].id)

        if timeout:
            self.bot.scheduler.schedule_in(message_delete_timeout(), time=timeout)
        else:
            self.bot.scheduler.schedule_in(message_delete_timeout(), time=300)

    @BaseService.listener(Events.on_reaction_add)
    async def delete_message(
        self, reaction: discord.Reaction, user: discord.User | discord.Member
    ) -> None:
        role_ids = [role.id for role in user.roles] if isinstance(user, discord.Member) else []
        delete = False

        if reaction.emoji != "🗑️" or reaction.message.id not in self.messages:
            return
        elif await self.bot.claim_route.check_claim_user(
            Claims.delete_message, t.cast(discord.Member, user)
        ):
            delete = True
        elif user.id == self.messages[reaction.message.id].author:
            delete = True
        elif isinstance(user, discord.Member):
            if user.guild_permissions.administrator:
                delete = True
            elif any(
                True for role in self.messages[reaction.message.id].roles if role.id in role_ids
            ):
                delete = True

        if delete:
            for msg in self.messages[reaction.message.id].message_to_delete:
                log.info("Message {message} deleted by delete message service", message=msg.id)
                await msg.delete()
            del self.messages[reaction.message.id]

    async def load_service(self) -> None:
        pass
