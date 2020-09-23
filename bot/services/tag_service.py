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

        name = found_name.groupdict()['name']
        
        if not await repo.check_tag_exists(name, message.guild.id):
            return

        content = await repo.get_tag_content(name, message.guild.id)
        await message.channel.send(content)

    async def load_service(self):
        pass
