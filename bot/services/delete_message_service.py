import logging
import typing as t
import asyncio

import discord

from bot.data.message_repository import MessageRepository
from bot.services.base_service import BaseService
from bot.messaging.events import Events
from bot.messaging import messenger

log = logging.getLogger(__name__)


class DeleteMessageService(BaseService):
    """
    This service allows for messages sent by the bot to be deleted
    The messags by default are allowed by deleted by admins and the person who called the bot
    """

    def __init__(self, *, bot):
        super().__init__(bot)
        self.messages = {}

    # Called When a cog would like to be able to delete a message or messages
    @BaseService.Listener(Events.on_set_deletable)
    async def set_message_deletable(self, *,
                                    msg: t.List[discord.Message],
                                    roles: t.List[discord.Role] = [],
                                    author: discord.Member = None,
                                    timeout: int = None):

        if not isinstance(msg , t.List):
            msg = [msg]
        if not isinstance(roles , t.List):
            roles = [roles]

        # stores the message info
        self.messages[msg[-1].id] = {
            "MessagesToDelete": msg,
            "Roles": roles,
            "Author": author.id if author else None
        }

        # the emoji is placed on the last message in the list
        await msg[-1].add_reaction("🗑️")
        if timeout:
            await asyncio.sleep(timeout) 
            try:
                await msg[-1].clear_reactions()
                del self.messages[msg[-1].id]
            except:
                pass
            finally:
                log.info(f'Message: {msg[-1].id} timed out as deletable')

    @BaseService.Listener(Events.on_reaction_add)
    async def delete_message(self, reaction: discord.Reaction, user: t.Union[discord.User, discord.Member]):
        role_ids = [role.id for role in user.roles]
        delete = False

        if reaction.emoji != "🗑️" or reaction.message.id not in self.messages:
            return
        elif user.guild_permissions.administrator:
            delete = True
        elif user.id == self.messages[reaction.message.id]["Author"]:
            delete = True
        elif any(True for role in self.messages[reaction.message.id]["Roles"] if role.id in role_ids):
            delete = True

        if delete:
            for msg in self.messages[reaction.message.id]["MessagesToDelete"]:
                log.info(f"Mesaage {msg.id} deleted by delete message service")
                await msg.delete()
            del self.messages[reaction.message.id]

    async def load_service(self):
        pass
