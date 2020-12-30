import logging
import re

import discord

from bot.services.base_service import BaseService
from bot.messaging.events import Events
from bot.data.tag_repository import TagRepository
from bot.services.starboard_service import StarboardService

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
        
        validTagFound = False
        if not found_name:
            return

        tagsContent = ''
        
        for match in re.finditer('(^| ?)[$](\w+)($| )', message.content, re.S):
            end = match.end()
            
            name = found_name.groupdict()['name'].lower()
            if not await repo.check_tag_exists(name, message.guild.id):
                found_name = re.search(pattern, message.content[end: ])
                continue
            validTagFound = True
            tagsContent += await repo.get_tag_content(name, message.guild.id) + '\n'
            await repo.increment_tag_use_counter(name, message.guild.id)
            log.info(f'Tag "{found_name}" invoked in guild: {message.guild.id} by: {message.author.id}')
                    
            found_name = re.search(pattern, message.content[end: ])
            if(found_name):
                tagsContent += '-----\n'

        if not validTagFound:
            return
            
        pages = []

        #If length of all tags is greater than the threshold, sends it to the paginate service, otherwise sends as a normal message
        for i, chunk in enumerate(StarboardService.chunk_iterable(self, tagsContent, 500)):
            pages.append(chunk)

        if len(pages) > 1:
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
