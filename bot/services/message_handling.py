import logging

import discord

from bot.messaging.events import Events
from bot.services.base_service import BaseService
from bot.consts import DesignatedChannels, Colors
from bot.data.message_repository import MessageRepository
import bot.messaging.messenger as messenger

log = logging.getLogger(__name__)

class MessageHandling(BaseService):

    def __init__(self, *, bot):
        super().__init__(bot)

    @BaseService.Listener(Events.on_message_recieved)
    async def on_message_recieved(self, message) -> None:
        log.info(f'Message from {message.author}: {message.content} in guild {message.guild.id}')

        if self.bot.user.mentioned_in(message) and message.mention_everyone is False:
            await message.channel.send('Hello there everyone!!')
        
        await self.bot.process_commands(message)
        await MessageRepository().add_message(message)

    @BaseService.Listener(Events.on_message_edit)
    async def on_message_edit(self, before, after):
        log.info(f'Message edited in #{before.channel.name} By: \
         {self.get_full_name(before.author)} \nBefore: {before.content} \nAfter: {after.content}')

        embed = discord.Embed(title= f':repeat: **Message Edited in #{before.channel.name}**', color= Colors.ClemsonOrange)
        embed.add_field(name= f'Message Link', value= f'[Click Here]({after.jump_url})')
        embed.add_field(name= 'Before', value= f'```{before.content}```', inline= False)
        embed.add_field(name= 'After', value= f'```{after.content}```', inline= False)
        embed.set_footer(text=f'{self.get_full_name(before.author)}', icon_url= before.author.avatar_url)

        await messenger.publish(Events.on_send_in_designated_channel, DesignatedChannels.message_log, embed)

    @BaseService.Listener(Events.on_message_delete)
    async def on_message_delete(self, message):
        log.info(f'Message deleted in #{message.channel.name} by {self.get_full_name(message.author)}: {message.content}')

        embed = discord.Embed(title= f':wastebasket: **Message Deleted in #{message.channel.name}**', color= Colors.ClemsonOrange)
        embed.add_field(name= 'Message', value= f'```{message.content}```', inline= False)
        embed.set_footer(text=f'{self.get_full_name(message.author)}', icon_url= message.author.avatar_url)

        await messenger.publish(Events.on_send_in_designated_channel, DesignatedChannels.message_log, embed)

    def get_full_name(self, author) -> str: 
        return f'{author.name}#{author.discriminator}' 

    async def load_service(self):
        pass
