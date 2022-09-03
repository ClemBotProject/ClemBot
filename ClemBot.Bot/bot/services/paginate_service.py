import asyncio
import typing as t
from dataclasses import dataclass

import discord
from discord.ext.commands.errors import BadArgument

from bot.clem_bot import ClemBot
from bot.consts import Colors
from bot.messaging.events import Events
from bot.services.base_service import BaseService
from bot.utils.logging_utils import get_logger

log = get_logger(__name__)


@dataclass
class Message:
    pages: t.Union[list[discord.Embed], list[str]]
    _curr_page_num: int
    author: int
    footers: list[str]
    embed_name: t.Optional[str] = None
    field_title: t.Optional[str] = None

    @property
    def curr_page_num(self) -> int:
        return self._curr_page_num

    @curr_page_num.setter
    def curr_page_num(self, page_num: int) -> None:
        self._curr_page_num = page_num

    @property
    def curr_page(self) -> t.Union[discord.Embed, str]:
        return self.pages[self._curr_page_num]

    @property
    def curr_content(self) -> discord.Embed:

        page = self.curr_page
        if isinstance(page, discord.Embed):
            page.set_footer(
                text=f"{self.footers[self._curr_page_num]}\nPage {self.curr_page_num + 1} of {len(self.pages)}"
            )
            return page
        elif not isinstance(page, str):
            raise BadArgument(
                f"Embed or string expected in the paginator service: {type(page)} found"
            )

        embed = discord.Embed(title=self.embed_name, color=Colors.ClemsonOrange)
        embed.add_field(name=self.field_title, value=self.pages[self._curr_page_num])
        embed.set_footer(text=f"Page {self.curr_page_num + 1} of {len(self.pages)}")
        return embed


class PaginateService(BaseService):
    """
    This service allows for messages sent by the bot to be paginated
    """

    def __init__(self, *, bot: ClemBot):
        super().__init__(bot)
        self.messages = dict[int, Message]()
        self.reactions = ["⏮️", "⬅️", "➡️", "⏭️"]

    # Called When a cog would like to be able to paginate a message
    @BaseService.listener(Events.on_set_pageable_text)
    async def set_text_pageable(
        self,
        *,
        embed_name: str,
        field_title: str,
        pages: list[str] | str,
        author: discord.Member,
        channel: discord.TextChannel,
        timeout: int = 60,
    ) -> None:

        if not isinstance(pages, list):
            pages = [pages]

        if not all(isinstance(p, str) for p in pages):
            raise BadArgument("All paginate text pages need to be of type string")

        embed = discord.Embed(title=embed_name, color=Colors.ClemsonOrange)
        # set the first page of the embed
        embed.add_field(name=field_title, value=pages[0])
        embed.set_footer(text=f"Page 1 of {len(pages)}")
        msg = await channel.send(embed=embed)

        # stores the message info
        message = Message(
            pages, 0, author.id, embed_name=embed_name, field_title=field_title, footers=[]
        )
        self.messages[msg.id] = message
        await self.send_scroll_reactions(msg, author, timeout)

    @BaseService.listener(Events.on_set_pageable_embed)
    async def set_embed_pageable(
        self,
        *,
        pages: list[discord.Embed],
        author: discord.Member,
        channel: discord.TextChannel,
        timeout: int = 60,
    ) -> None:

        if not isinstance(pages, list):
            pages = [pages]

        pages = [e.copy() for e in pages]

        if not all(isinstance(p, discord.Embed) for p in pages):
            raise BadArgument("All paginate embed pages need to be of type discord.Embed")

        footers = []
        for embed in pages:
            if embed.footer is not None and embed.footer.text is not None:
                footers.append(embed.footer.text)

        message = Message(pages, 0, author.id, footers=footers)

        if len(footers) > 0:
            pages[0].set_footer(text=f"{footers[0]}\nPage 1 of {len(pages)}")
        # send the first initial embed
        msg = await channel.send(embed=pages[0])
        await self.bot.messenger.publish(Events.on_set_deletable, msg=msg, author=author)

        # stores the message info
        self.messages[msg.id] = message
        await self.send_scroll_reactions(msg, author, timeout)

    async def send_scroll_reactions(
        self, msg: discord.Message, author: discord.Member, timeout: int
    ) -> None:
        # add every emoji from the reaction list
        for reaction in self.reactions:
            await msg.add_reaction(reaction)

        await self.bot.messenger.publish(Events.on_set_deletable, msg=msg, author=author)

        if timeout:
            await asyncio.sleep(timeout)
            try:
                for reaction in self.reactions:
                    await msg.clear_reaction(reaction)
                del self.messages[msg.id]
            except:
                pass
            finally:
                log.info("Message: {msg_id} timed out as pageable", msg_id=msg.id)

    @BaseService.listener(Events.on_reaction_add)
    async def change_page(self, reaction: discord.Reaction, user: discord.Member) -> None:

        # check if emoji matches and user has perm to change page
        if reaction.emoji not in self.reactions or reaction.message.id not in self.messages.keys():
            return

        msg = self.messages[reaction.message.id]

        if not user.guild_permissions.administrator and not user.id == msg.author:
            return

        # check what emoji the user used
        if reaction.emoji == "⏮️":
            if msg.curr_page_num != 0:
                msg.curr_page_num = 0
        elif reaction.emoji == "⬅️":
            if msg.curr_page_num != 0:
                msg.curr_page_num -= 1
        elif reaction.emoji == "➡️":
            if msg.curr_page_num < len(msg.pages) - 1:
                msg.curr_page_num += 1
        elif reaction.emoji == "⏭️":
            if msg.curr_page_num != len(msg.pages) - 1:
                msg.curr_page_num = len(msg.pages) - 1

        await reaction.message.edit(embed=msg.curr_content)
        await reaction.message.remove_reaction(reaction.emoji, t.cast(discord.abc.Snowflake, user))

    async def load_service(self) -> None:
        pass
