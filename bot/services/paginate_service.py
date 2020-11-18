import logging
import typing as t
import asyncio
from dataclasses import dataclass

import discord

from bot.consts import Colors
from bot.data.message_repository import MessageRepository
from bot.services.base_service import BaseService
from bot.messaging.events import Events
from bot.messaging import messenger

log = logging.getLogger(__name__)

@dataclass
class Message:
    embed_name: str
    field_title: str
    pages: t.List[str]
    _curr_page: int
    author: int

    @property
    def curr_page(self):
        return self._curr_page

    @curr_page.setter
    def curr_page(self, page: int):
        self._curr_page = page

    @property
    def curr_content(self):
        return self.pages[self._curr_page]

class PaginateService(BaseService):
    """
    This service allows for messages sent by the bot to be paginated
    """

    def __init__(self, *, bot):
        super().__init__(bot)
        self.messages = {}
        self.reactions = ["⏮️","⬅️","➡️","⏭️"]

    # Called When a cog would like to be able to paginate a message
    @BaseService.Listener(Events.on_set_pageable)
    async def set_message_pageable(self, *,
                                    embed_name: str,
                                    field_title: str,
                                    pages: t.List[str],
                                    author: discord.Member = None,
                                    channel: discord.TextChannel,
                                    timeout: int = 60):

        if not isinstance(pages , t.List):
            pages = [pages]

        embed = discord.Embed(title= embed_name, color= Colors.ClemsonOrange)
        # set the first page of the embed
        embed.add_field(name= field_title, value= pages[0])
        embed.set_footer(text=f'Page 1 of {len(pages)}')
        msg = await channel.send(embed= embed)
        await self.bot.messenger.publish(Events.on_set_deletable, msg=msg, author=msg.author)

        # stores the message info
        message = Message(embed_name, field_title, pages, 0, author.id if author else None)
        self.messages[msg.id] = message

        # add every emoji from the reaction list
        for reaction in self.reactions:
            await msg.add_reaction(reaction)

        if timeout:
            await asyncio.sleep(timeout) 
            try:
                for reaction in self.reactions:
                    await msg.clear_reaction(reaction)
                del self.messages[msg.id]
            except:
                pass
            finally:
                log.info(f'Message: {msg.id} timed out as pageable')

    @BaseService.Listener(Events.on_reaction_add)
    async def change_page(self, reaction: discord.Reaction, user: t.Union[discord.User, discord.Member]):
        msg = self.messages[reaction.message.id]

        # check if emoji matches and user has perm to change page
        if reaction.emoji not in self.reactions or reaction.message.id not in self.messages:
            return
        if not user.guild_permissions.administrator and not user.id == msg.author:
            return

        embed = discord.Embed(title =  msg.embed_name, color=Colors.ClemsonOrange)

        # check what emoji the user used
        if reaction.emoji == "⏮️":
            if msg.curr_page != 0:
                msg.curr_page = 0
        elif reaction.emoji == "⬅️":
            if msg.curr_page != 0:
                msg.curr_page -= 1
        elif reaction.emoji == "➡️":
            if msg.curr_page < len(msg.pages)-1:
                msg.curr_page += 1
        elif reaction.emoji == "⏭️":
            if msg.curr_page != len(msg.pages)-1:
                msg.curr_page = len(msg.pages) - 1

        # edits the message and reset emoji (only user that triggered the action)
        embed.add_field(name= msg.field_title, value=msg.curr_content)
        embed.set_footer(text=f'Page {msg.curr_page+1} of {len(msg.pages)}')
        await reaction.message.edit(embed = embed)
        await reaction.message.remove_reaction(reaction.emoji, user)

    async def load_service(self):
        pass
