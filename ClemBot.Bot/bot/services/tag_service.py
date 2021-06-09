import logging
import re

import discord

from bot.messaging.events import Events
from bot.services.base_service import BaseService

log = logging.getLogger(__name__)

TAG_PREFIX = '$'
TAG_PAGINATE_THRESHOLD = 500


class TagService(BaseService):

    def __init__(self, *, bot):
        super().__init__(bot)

    @BaseService.Listener(Events.on_guild_message_received)
    async def on_guild_message_received(self, message: discord.Message) -> None:

        tags_content = []
        tag_found = False
        pattern = re.compile(f'(^|\\s)[{TAG_PREFIX}](\\w+)')
        for match in set(i[1] for i in pattern.findall(message.content)):
            tag = await self.bot.tag_route.get_tag(message.guild.id, match)

            if not tag:
                continue

            tag_found = True

            # tags_content.append(await repo.get_tag_content(match, message.guild.id))
            tags_content.append(tag['content'])

            await self.bot.tag_route.add_tag_use(message.guild.id, match, message.channel.id, message.author.id)

            log.info(f'Tag "{match}" invoked in guild: {message.guild.id} by: {message.author.id}')

        if not tag_found:
            return

        tag_str = '\n-------\n'.join(tags_content)
        pages = []

        # If length of all tags is greater than the threshold, sends it to the paginate service, otherwise sends as a normal message
        if len(tags_content) > 1:
            for chunk in self.chunk_iterable(tag_str, TAG_PAGINATE_THRESHOLD):
                pages.append(chunk)

        if len(pages) > 1:
            await self.bot.messenger.publish(Events.on_set_pageable_text,
                                             embed_name='Tags Contents',
                                             field_title='Contents',
                                             pages=pages,
                                             author=message.author,
                                             channel=message.channel)

        msg = await message.channel.send(tag_str)
        await self.bot.messenger.publish(Events.on_set_deletable,
                                         msg=msg,
                                         author=message.author,
                                         timeout=60)

    @staticmethod
    def chunk_iterable(iterable, chunk_size):
        for i in range(0, len(iterable), chunk_size):
            yield iterable[i:i + chunk_size]

    async def load_service(self):
        pass
