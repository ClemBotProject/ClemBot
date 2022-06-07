import dataclasses
import datetime
import json
import logging
import re
from typing import Iterable

import discord

from bot.consts import Colors, DesignatedChannels, OwnerDesignatedChannels
from bot.messaging.events import Events
from bot.services.base_service import BaseService
import bot.utils.log_serializers as serializers

log = logging.getLogger(__name__)

MESSAGE_BATCH_SIZE = 20
MAX_QUOTED_CONTENT_SIZE = 1021  # 1024 - 3 (for content + '...')


@dataclasses.dataclass()
class MessageDto:
    id: int
    content: str
    guild: int
    author: int
    channel: int
    time: datetime.datetime


@dataclasses.dataclass()
class MessageEditDto:
    id: int
    content: str
    time: datetime.datetime


class MessageHandlingService(BaseService):

    def __init__(self, *, bot):
        super().__init__(bot)
        self.message_batch = {}
        self.message_edit_batch = []

    async def batch_send_message(self, message: discord.Message):
        """
        Batch the messages to send them all at once to
        the api to avoid sending hundreds a second
        """

        if len(self.message_batch) > MESSAGE_BATCH_SIZE:
            # Copy the list values and clear the batch list BEFORE
            # we send them. This way we can accept new messages while
            # the current batch is being sent
            batch_values = list(self.message_batch.values())
            self.message_batch.clear()

            await self.bot.message_route.batch_create_message(batch_values, raise_on_error=False)

        self.message_batch[message.id] = MessageDto(message.id,
                                                    message.content,
                                                    message.guild.id,
                                                    message.author.id,
                                                    message.channel.id,
                                                    datetime.datetime.utcnow())

    async def batch_send_message_edit(self, id: int, content: str):
        """
        Batch the message edits to send them all at once to
        the api to avoid sending hundreds a second
        """

        if message := self.message_batch.get(id, None):
            self.message_batch[message.id].content = content
            return

        if len(self.message_edit_batch) > MESSAGE_BATCH_SIZE:
            # Copy the list and clear the batch edit list BEFORE
            # we send them. This way we can accept new message edits while
            # the current batch is being sent
            batch_values = list(self.message_edit_batch)
            self.message_edit_batch.clear()

            await self.bot.message_route.batch_edit_message(batch_values, raise_on_error=False)

        self.message_edit_batch.append(MessageEditDto(id,
                                                      content,
                                                      datetime.datetime.utcnow()))

    @BaseService.Listener(Events.on_guild_message_received)
    async def on_guild_message_received(self, message: discord.Message) -> None:

        log.info('Message from {author}: "{content}" Guild {guild} Channel: {channel}',
                 author=serializers.log_user(message.author),
                 content=message.content,
                 guild=serializers.log_guild(message.guild),
                 channel=serializers.log_channel(message.channel))

        # Check if the message is a discord message link and check if this server has
        # Enabled embed message links
        await self.handle_message_links(message)

        # Primary entry point for handling commands
        await self.bot.process_commands(message)

        if not message.content:
            return

        await self.batch_send_message(message)

    @BaseService.Listener(Events.on_dm_message_received)
    async def on_dm_message_received(self, message: discord.Message) -> None:
        embed = discord.Embed(title=f'Bot Direct Message',
                              color=Colors.ClemsonOrange,
                              description=f'{message.content}')
        embed.set_footer(text=message.author, icon_url=message.author.display_avatar.url)

        log.info('Message from {author}: "{content}" Guild Unknown (DM)',
                 author=serializers.log_user(message.author),
                 content=message.content)

        await self.messenger.publish(Events.on_broadcast_designated_channel, OwnerDesignatedChannels.bot_dm_log, embed)
        await message.author.send(
            'Hello there, I dont currently support DM commands. Please run my commands in a server')  # https://discordpy.readthedocs.io/en/latest/faq.html#how-do-i-send-a-dm

    @BaseService.Listener(Events.on_message_edit)
    async def on_message_edit(self, before: discord.Message, after: discord.Message):
        # We do not want to track messages that have embeds inserted via links
        if before.content == after.content:
            return

        log.info('Message edited in #{channel} By: {author} \nBefore: {before_content} \nAfter: {after_content}',
                 channel=serializers.log_channel(before.channel),
                 author=serializers.log_user(after.author),
                 before_content=before.content,
                 after_content=after.content)

        await self.batch_send_message_edit(after.id, after.content)

        embed = discord.Embed(title=f':repeat: **Message Edited in #{before.channel.name}**',
                              color=Colors.ClemsonOrange)
        embed.add_field(name=f'Message Link', value=f'[Click Here]({after.jump_url})')

        before_chunk = self.split_string_chunks(before.content, 900)
        after_chunk = self.split_string_chunks(after.content, 900)

        for i, val in enumerate(before_chunk):
            embed.add_field(name='**Before**' if i == 0 else 'Cont...', value=f'```{val}```', inline=False)

        for i, val in enumerate(after_chunk):
            embed.add_field(name='**After**' if i == 0 else 'Cont...', value=f'```{val}```', inline=False)

        embed.set_footer(text=f'{self.get_full_name(before.author)}', icon_url=before.author.display_avatar.url)

        await self.bot.messenger.publish(Events.on_send_in_designated_channel,
                                         DesignatedChannels.message_log,
                                         after.guild.id,
                                         embed)

    # noinspection PyArgumentList
    @BaseService.Listener(Events.on_raw_message_edit)
    async def on_raw_message_edit(self, payload):

        message = await self.bot.message_route.get_message(payload.message_id)
        channel = self.bot.get_channel(payload.channel_id)

        try:
            if message is not None:
                log.info('Uncached message edited By: {author} \nBefore: {before} \nAfter: {after}',
                         author=message['userId'],
                         before=message['content'],
                         after=payload.data['content'])

                await self.batch_send_message_edit(message['id'], payload.data['content'])

                embed = discord.Embed(title=f':repeat: **Uncached message edited in #{channel.name}**',
                                      color=Colors.ClemsonOrange)

                before_chunk = self.split_string_chunks(message['content'], 900)
                after_chunk = self.split_string_chunks(payload.data['content'], 900)

                for i, val in enumerate(before_chunk):
                    embed.add_field(name='**Before**' if i == 0 else 'Cont...', value=f'```{val}```', inline=False)

                for i, val in enumerate(after_chunk):
                    embed.add_field(name='**After**' if i == 0 else 'Cont...', value=f'```{val}```', inline=False)

                embed.set_footer(text=f'Author id: {payload.data["author"]["id"]}')

                await self.bot.messenger.publish(Events.on_send_in_designated_channel,
                                                 DesignatedChannels.message_log,
                                                 int(payload.data['guild_id']),
                                                 embed)
            else:
                try:
                    log.info(f'Uncached message edited in #{channel.name} By: \
                        {payload.data["author"]["id"]} \nBefore: Unknown Content \nAfter: {payload.data["Content"]}')
                except KeyError:
                    log.info('Uncached invalid message event received: {data}', data=json.dumps(payload.data))

                embed = discord.Embed(title=f':repeat: **Uncached message edited in #{channel.name}**',
                                      color=Colors.ClemsonOrange)

                embed.add_field(name='Before', value='Unknown, message not stored in the database', inline=False)

                after_chunk = self.split_string_chunks(payload.data['content'], 900)
                for i, val in enumerate(after_chunk):
                    embed.add_field(name='**After**' if i == 0 else 'Cont...', value=f'```{val}```', inline=False)

                embed.set_footer(text=f'Author id: {payload.data["author"]["id"]}')

                await self.bot.messenger.publish(Events.on_send_in_designated_channel,
                                                 DesignatedChannels.message_log,
                                                 int(payload.data['guild_id']),
                                                 embed)
        except KeyError as e:
            log.error('raw_message_edit Error: {e} \n', e=e)

    @BaseService.Listener(Events.on_message_delete)
    async def on_message_delete(self, message: discord.Message):
        log.info('Uncached message deleted in #{channel} by {author}: {content}',
                 channel=serializers.log_channel(message.channel),
                 author=serializers.log_user(message.author),
                 content=message.content)

        embed = discord.Embed(title=f':wastebasket: **Message Deleted in #{message.channel.name}**',
                              color=Colors.ClemsonOrange)

        message_chunk = self.split_string_chunks(message.content, 900)
        for i, val in enumerate(message_chunk):
            embed.add_field(name='**Message**' if i == 0 else 'Cont...', value=f'```{val}```', inline=False)

        embed.set_footer(text=f'{self.get_full_name(message.author)}', icon_url=message.author.display_avatar.url)

        await self.bot.messenger.publish(Events.on_send_in_designated_channel,
                                         DesignatedChannels.message_log,
                                         message.guild.id,
                                         embed)

    @BaseService.Listener(Events.on_raw_message_delete)
    async def on_raw_message_delete(self, payload):

        message = await self.bot.message_route.get_message(payload.message_id)
        channel = self.bot.get_channel(payload.channel_id)

        log.info(f'Uncached message deleted id:{payload.message_id} in #{channel.name}')

        if message is not None:
            embed = discord.Embed(title=f':wastebasket: **Uncached message deleted in #{channel.name}**',
                                  color=Colors.ClemsonOrange)
            message_chunk = self.split_string_chunks(message['content'], 900)
            for i, val in enumerate(message_chunk):
                embed.add_field(name='**Message**' if i == 0 else 'Cont...', value=f'```{val}```', inline=False)
        else:
            embed = discord.Embed(title=f':wastebasket: **Uncached message deleted in #{channel.name}**',
                                  color=Colors.ClemsonOrange)
            embed.add_field(name='Message', value='Unknown, message not in the database', inline=False)

        await self.bot.messenger.publish(Events.on_send_in_designated_channel,
                                         DesignatedChannels.message_log,
                                         int(payload.guild_id),
                                         embed)

    async def handle_message_links(self, message: discord.Message) -> None:
        """
        Searches all incoming messages for a discord message link and replies to the 
        context with that message

        Args:
            message (discord.Message): the original message containing the link
        """

        pattern = r'(.+)?http(s)?:\/\/(www.)?discord(app)?.com\/channels\/(?P<guild_id>\d{18})\/(?P<channel_id>\d{18})\/(?P<message_id>\d{18})\n*(.+)?'  # noqa: E501

        result = re.search(pattern, message.content)

        if not result:
            return

        if not await self.bot.guild_route.get_can_embed_link(message.guild.id):
            return

        matches = result.groupdict()
        avi = message.author.display_avatar.url
        source_channel = message.channel
        link_channel = await self.bot.fetch_channel(matches['channel_id'])
        link_message = await link_channel.fetch_message(matches['message_id'])
        has_reply = message.reference is not None
        # result.group(1) and result.group(8) can return None, so we check both != None and len()
        raw_text = (bool(result.group(1)) and len(result.group(1)) != 0) or \
                   (bool(result.group(8)) and len(result.group(8)) != 0)

        if len(link_message.embeds) > 0:
            embed = link_message.embeds[0]
            full_name = f'{self.get_full_name(message.author)}'
            embed.add_field(name=f'Quoted by:', value=f'{full_name} from [Click Me]({link_message.jump_url})')
            if not has_reply and not raw_text:
                await message.delete()
            msg = await source_channel.send(embed=embed)
            await self.bot.messenger.publish(Events.on_set_deletable, msg=msg, author=message.author, timeout=60)
            return

        embed = discord.Embed(title=f'Message linked from #{link_channel.name}', color=Colors.ClemsonOrange)
        embed.set_author(name=f'Quoted by: {self.get_full_name(message.author)}', icon_url=avi)

        if link_message.content:
            if len(link_message.content) < MAX_QUOTED_CONTENT_SIZE:
                embed.add_field(name='Content', value=link_message.content, inline=False)
            else:
                embed.add_field(name='Content',
                                value=link_message.content[0:MAX_QUOTED_CONTENT_SIZE] + '...',
                                inline=False)

        image = None
        if link_message.attachments:
            att = link_message.attachments[0]
            image = att.proxy_url
            embed.add_field(name="Attachments", value=f"[{att.filename}]({att.url})", inline=False)

        if image:
            embed.set_image(url=image)
        embed.add_field(name='Author', value=f'{self.get_full_name(link_message.author)}', inline=True)
        embed.add_field(name='Message Link', value=f'[Click Me]({link_message.jump_url})', inline=True)

        reply_to = None
        if has_reply:
            reply_to = message.reference
        elif raw_text and not has_reply:
            reply_to = message

        msg = await source_channel.send(embed=embed, reference=reply_to)
        if not raw_text:
            await message.delete()
        await self.bot.messenger.publish(Events.on_set_deletable, msg=msg, author=message.author, timeout=60)

    def get_full_name(self, author) -> str:
        return f'{author.name}#{author.discriminator}'

    def split_string_chunks(self, string: str, n: int) -> Iterable[str]:
        return (string[i: i + n] for i in range(0, len(string), n))

    async def load_service(self):
        pass
