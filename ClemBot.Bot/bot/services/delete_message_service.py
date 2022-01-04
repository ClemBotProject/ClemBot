import asyncio
import logging
import typing as t

import discord

from bot.consts import Claims
from bot.messaging.events import Events
from bot.services.base_service import BaseService

log = logging.getLogger(__name__)


class DeleteMessageService(BaseService):
    """
    This service allows for messages sent by the bot to be deleted
    The messages by default are allowed by deleted by admins and the person who called the bot
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

        if not isinstance(msg, t.List):
            msg = [msg]
        if not isinstance(roles, t.List):
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
                await msg[-1].clear_reaction("🗑️")
                del self.messages[msg[-1].id]
            except:
                pass
            finally:
                log.info('Message: {message} timed out as deletable', message=msg[-1].id)

    @BaseService.Listener(Events.on_reaction_add)
    async def delete_message(self, reaction: discord.Reaction, user: t.Union[discord.User, discord.Member]):
        role_ids = [role.id for role in user.roles]
        delete = False

        if reaction.emoji != '🗑️' or reaction.message.id not in self.messages:
            return
        elif await self.bot.claim_route.check_claim_user(Claims.delete_message, user):
            delete = True
        elif user.guild_permissions.administrator:
            delete = True
        elif user.id == self.messages[reaction.message.id]['Author']:
            delete = True
        elif any(True for role in self.messages[reaction.message.id]['Roles'] if role.id in role_ids):
            delete = True

        if delete:
            for msg in self.messages[reaction.message.id]['MessagesToDelete']:
                log.info('Message {message} deleted by delete message service', message=msg.id)
                await msg.delete()
            del self.messages[reaction.message.id]

    async def load_service(self):
        pass
