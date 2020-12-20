import logging
import re

import discord

from bot.services.base_service import BaseService
from bot.messaging.events import Events
from bot.data.tag_repository import TagRepository

log = logging.getLogger(__name__)

TAG_PREFIX = '$'
TAG_PAGINATE_THRESHOLD = 500


class TagService(BaseService):

    def __init__(self, *, bot):
        super().__init__(bot)
    
    @BaseService.Listener(Events.on_message_recieved)
    async def on_message_recieved(self, message: discord.Message) -> None:
        repo = TagRepository()

        pattern = f'(^| )[{TAG_PREFIX}](?P<name>\\w+)($| )'
        found_name = re.search(pattern, message.content)
        
        if not found_name:
            return
        
        searchIndex = 0

        tagsContent = ''
        remainingMessage = message.content
        while found_name:
            name = found_name.groupdict()['name'].lower()
            
            
            if not await repo.check_tag_exists(name, message.guild.id):
                return
            tagsContent += await repo.get_tag_content(name, message.guild.id) + '\n'
            await repo.increment_tag_use_counter(name, message.guild.id)
            log.info(f'Tag "{found_name}" invoked in guild: {message.guild.id} by: {message.author.id}')
                    
            try:
                searchIndex = remainingMessage.index(TAG_PREFIX) + 1
                remainingMessage = remainingMessage[searchIndex: ]
                found_name = re.search(pattern, remainingMessage)
            except ValueError: 
                found_name = False
        if len(tagsContent) > TAG_PAGINATE_THRESHOLD:
            pages = []
            lowerBound = 0
            higherBound = TAG_PAGINATE_THRESHOLD

            while lowerBound < len(tagsContent):
                pages.append(tagsContent[lowerBound:higherBound])
                lowerBound = higherBound
                higherBound += TAG_PAGINATE_THRESHOLD

            await self.bot.messenger.publish(Events.on_set_pageable,
                    embed_name='Tags Contents',
                    field_title='Contents',
                    pages = pages,
                    author=message.author,
                    channel=message.channel)
        else:
            msg = await message.channel.send(tagsContent)
            await self.bot.messenger.publish(Events.on_set_deletable, 
                msg=msg, 
                author= message.author, 
                timeout=60)
            

    async def load_service(self):
        pass
