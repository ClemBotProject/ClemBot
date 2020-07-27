import logging
import re

import discord

import bot.messaging.messenger as messenger
from bot.consts import Colors, DesignatedChannels
from bot.data.message_repository import MessageRepository
from bot.messaging.events import Events
from bot.services.base_service import BaseService

log = logging.getLogger(__name__)

class MessageHandlingService(BaseService):

    def __init__(self, *, bot):
        super().__init__(bot)

    @BaseService.Listener(Events.on_message_recieved)
    async def on_message_recieved(self, message: discord.Message) -> None:
        log.info(f'Message from {message.author}: {message.content} in guild {message.guild.id}')

        if self.bot.user.mentioned_in(message) and message.mention_everyone is False:
            await message.channel.send('Hello there everyone!!')

        await self.handle_message_links(message)

        #Primary entry point for handling commands
        await self.bot.process_commands(message)

        await MessageRepository().add_message(message)

    @BaseService.Listener(Events.on_message_edit)
    async def on_message_edit(self, before: discord.Message, after: discord.Message):
        log.info(f'Message edited in #{before.channel.name} By: \
            {self.get_full_name(before.author)} \nBefore: {before.content} \nAfter: {after.content}')

        await MessageRepository().edit_message_content(after.id, after.content)

        embed = discord.Embed(title= f':repeat: **Message Edited in #{before.channel.name}**', color= Colors.ClemsonOrange)
        embed.add_field(name= f'Message Link', value= f'[Click Here]({after.jump_url})')
        embed.add_field(name= 'Before', value= f'```{before.content}```', inline= False)
        embed.add_field(name= 'After', value= f'```{after.content}```', inline= False)
        embed.set_footer(text=f'{self.get_full_name(before.author)}', icon_url= before.author.avatar_url)

        await messenger.publish(Events.on_send_in_designated_channel,
                DesignatedChannels.message_log, 
                after.guild.id, 
                embed)
    
    @BaseService.Listener(Events.on_raw_message_edit)
    async def on_raw_message_edit(self, payload):

        message_repo = MessageRepository()
        message = await message_repo.get_message(payload.message_id)
        channel = self.bot.get_channel(payload.channel_id)
        
        if message is not None:
            log.info(f'Uncached message edited in #{channel.name} By: \
                {message["fk_authorId"]} \nBefore: {message["content"]} \nAfter: {payload.data["content"]}')

            await message_repo.edit_message_content(message['id'], payload.data['content'])

            embed = discord.Embed(title= f':repeat: **Uncached message edited in #{channel.name}**',
                color= Colors.ClemsonOrange)

            embed.add_field(name= 'Before', value= f'```{message["content"]}```', inline= False)
            embed.add_field(name= 'After', value= f'```{payload.data["content"]}```', inline= False)
            embed.set_footer(text=f'Author id: {payload.data["author"]["id"]}')

            await messenger.publish(Events.on_send_in_designated_channel, DesignatedChannels.message_log, embed)
        else:
            log.info(f'Uncached message edited in #{channel.name} By: \
                {payload.data["author"]["id"]} \nBefore: Unknown Content \nAfter: {payload.data["content"]}')

            embed = discord.Embed(title= f':repeat: **Uncached message edited in #{channel.name}**',
                color= Colors.ClemsonOrange)

            embed.add_field(name= 'Before', value= 'Unknown, message not stored in the database', inline= False)
            embed.add_field(name= 'After', value= f'```{payload.data["content"]}```', inline= False)
            embed.set_footer(text=f'Author id: {payload.data["author"]["id"]}')

            await messenger.publish(Events.on_send_in_designated_channel,
                    DesignatedChannels.message_log, 
                    payload.guild.id,
                    embed)

    @BaseService.Listener(Events.on_message_delete)
    async def on_message_delete(self, message: discord.Message):
        log.info(f'Uncached message deleted in #{message.channel.name} by \
            {self.get_full_name(message.author)}: {message.content}')

        await MessageRepository().set_message_deletion(message.id)

        embed = discord.Embed(title= f':wastebasket: **Message Deleted in #{message.channel.name}**',
            color= Colors.ClemsonOrange)
        embed.add_field(name= 'Message', value= f'```{message.content}```', inline= False)
        embed.set_footer(text=f'{self.get_full_name(message.author)}', icon_url= message.author.avatar_url)

        await messenger.publish(Events.on_send_in_designated_channel,
                DesignatedChannels.message_log,
                message.guild.id,
                embed)

    @BaseService.Listener(Events.on_raw_message_delete)
    async def on_raw_message_delete(self, payload):

        message_repo = MessageRepository()
        message = await message_repo.get_message(payload.message_id)
        channel = self.bot.get_channel(payload.channel_id)

        log.info(f'Uncached message deleted id:{payload.message_id} in #{channel.name}')

        await message_repo.set_message_deletion(payload.message_id)

        if message is not None:
            embed = discord.Embed(title= f':wastebasket: **Uncached message deleted in #{channel.name}**',
                color= Colors.ClemsonOrange)
            embed.add_field(name= 'Message', value= f'```{message["content"]}```', inline= False)
        else:
            embed = discord.Embed(title= f':wastebasket: **Uncached message deleted in #{channel.name}**',
                color= Colors.ClemsonOrange)
            embed.add_field(name= 'Message', value= 'Unknown, message not in the database', inline= False)

        await messenger.publish(Events.on_send_in_designated_channel, 
                DesignatedChannels.message_log, 
                payload.guild.id,
                embed)
    
    async def handle_message_links(self, message: discord.Message) -> None:
        """
        Searches all incoming messages for a discord message link and replies to the 
        context with that message

        Args:
            message (discord.Message): the original message containing the link
        """

        pattern = r'^http(s)?:\/\/(www.)?discord(app)?.com\/channels\/(?P<guild_id>\d{18})\/(?P<channel_id>\d{18})\/(?P<message_id>\d{18})$'  # noqa: E501
        
        result = re.search(pattern, message.content)
        if result:
            matches = result.groupdict()
            avi = message.author.avatar_url_as(static_format= 'png')

            source_channel = message.channel
            link_channel = await self.bot.fetch_channel(matches['channel_id'])
            link_message = await link_channel.fetch_message(matches['message_id'])

            embed = discord.Embed(title=f'Message linked from #{link_channel.name}', color= Colors.ClemsonOrange)
            embed.set_author(name= f'Quoted by: {self.get_full_name(message.author)}', icon_url= avi)
            embed.add_field(name= 'Content', value= f'`{link_message.content}`', inline= False)
            embed.add_field(name= 'Author', value= f'{self.get_full_name(link_message.author)}', inline= True)
            embed.add_field(name= 'Message Link', value= f'[Click Me]({link_message.jump_url})', inline= True)

            await message.delete()
            await source_channel.send(embed= embed)

    def get_full_name(self, author) -> str: 
        return f'{author.name}#{author.discriminator}' 
    
    async def load_service(self):
        pass
