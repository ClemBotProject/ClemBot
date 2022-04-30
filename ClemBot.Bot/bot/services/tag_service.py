import logging
import re

import discord

from bot.clem_bot import ClemBot
from bot.messaging.events import Events
from bot.services.base_service import BaseService
import bot.utils.log_serializers as serializers
import bot.bot_secrets as bot_secrets
from bot.errors import PrefixRequestError

log = logging.getLogger(__name__)

TAG_PAGINATE_THRESHOLD = 500
TAG_PREFIX_DEFAULT = '$'

class TagService(BaseService):

    def __init__(self, *, bot):
        super().__init__(bot)

    @BaseService.Listener(Events.on_guild_message_received)
    async def on_guild_message_received(self, message: discord.Message) -> None:

        tagprefix = await self.get_tag_prefix(self.bot, message=message)
        if tagprefix is None:
            return
        
        tagprefix = tagprefix[0]
        tags_content = []
        tag_found = False
        pattern = re.compile(fr'(^|\s)[{re.escape(tagprefix)}](\w+)')
        for match in set(i[1] for i in pattern.findall(message.content)):
            tag = await self.bot.tag_route.get_tag(message.guild.id, match)

            if not tag:
                continue

            tag_found = True

            tags_content.append(tag.content)

            await self.bot.tag_route.add_tag_use(message.guild.id, match, message.channel.id, message.author.id)

            log.info('Tag "{match}" invoked in guild: {guild} by: {author}',
                     match=match,
                     guild=serializers.log_guild(message.author.guild),
                     author=serializers.log_user(message.author))

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

    async def get_tag_prefix(self, bot: ClemBot, message: discord.Message):

        tagprefixes = []

        # Check if bot is in BotOnly mode, if it is we cant get custom tag prefixes
        # so we have to fall back to self.default
        if not bot_secrets.secrets.bot_only:
            # noinspection PyBroadException
            try:
                # Try to grab the tag prefixes from the db, raise an error on failure
                # and bailout, we cant respond to anything at the moment
                tagprefixes = await bot.custom_tag_prefix_route.get_custom_tag_prefixes(message.guild.id, raise_on_error=True)
            except Exception as e:
                # if the api call fails for any reason then we bail out and return nothing 
                # so as to not spam the servers with error messages on every message. 
                # failing silently is preferable to that
                return None
                
        if len(tagprefixes) == 0:
            tagprefixes = [TAG_PREFIX_DEFAULT]

        return tagprefixes

    @staticmethod
    def chunk_iterable(iterable, chunk_size):
        for i in range(0, len(iterable), chunk_size):
            yield iterable[i:i + chunk_size]

    async def load_service(self):
        pass
