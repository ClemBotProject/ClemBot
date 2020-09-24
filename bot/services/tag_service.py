import logging
import re

import discord

from bot.services.base_service import BaseService
from bot.messaging.events import Events
from bot.data.tag_repository import TagRepository

log = logging.getLogger(__name__)

TAG_PREFIX = '$'

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

        name = found_name.groupdict()['name'].lower()
        
        if not await repo.check_tag_exists(name, message.guild.id):
            return

        content = await repo.get_tag_content(name, message.guild.id)
        log.info(f'Tag "{found_name}" invoked in guild: {message.guild.id} by: {message.author.id}')
        msg = await message.channel.send(content)
        await self.bot.messenger.publish(Events.on_set_deletable, 
                msg=msg, 
                author= msg.author, 
                timeout=60)

    async def load_service(self):
        pass
