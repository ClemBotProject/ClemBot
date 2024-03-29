import re
import typing as t

import discord

import bot.bot_secrets as bot_secrets
import bot.utils.log_serializers as serializers
from bot.clem_bot import ClemBot
from bot.messaging.events import Events
from bot.services.base_service import BaseService
from bot.utils.helpers import chunk_sequence
from bot.utils.logging_utils import get_logger

log = get_logger(__name__)

TAG_PAGINATE_THRESHOLD = 500
TAG_PREFIX_DEFAULT = "$"


class TagService(BaseService):
    def __init__(self, *, bot: ClemBot):
        super().__init__(bot)

    @BaseService.listener(Events.on_guild_message_received)
    async def on_guild_message_received(self, message: discord.Message) -> None:
        tag_prefix: list[str] | str | None = await self.get_tag_prefixes(self.bot, message=message)
        if tag_prefix is None:
            return

        tag_prefix = tag_prefix[0]

        tags_contents = []

        # find all tag matches in the message content
        pattern = re.compile(rf"(^|\s){re.escape(tag_prefix)}(\w+)")
        for match in set(i[1] for i in pattern.findall(message.content)):

            if not message.guild:
                return

            tag = await self.bot.tag_route.get_tag(message.guild.id, match)

            if not tag:
                continue

            tags_contents.append(tag.content)

            await self.bot.tag_route.add_tag_use(
                message.guild.id, match, message.channel.id, message.author.id
            )

            log.info(
                'Tag "{match}" invoked in guild: {guild} by: {author}',
                match=match,
                guild=serializers.log_guild(t.cast(discord.Member, message.author).guild),
                author=serializers.log_user(message.author),
            )

        # check if there were no matched tags
        if not tags_contents:
            return

        tags_str = "\n-------\n".join(tags_contents)

        # if there is more than one tag invoked, check if we should paginate
        if len(tags_contents) > 1:
            # check if there's more than one page of tags, if there is we should paginate them
            if len(pages := list(chunk_sequence(tags_str, TAG_PAGINATE_THRESHOLD))) > 1:
                await self.bot.messenger.publish(
                    Events.on_set_pageable_text,
                    embed_name="Tags Contents",
                    field_title="Contents",
                    pages=pages,
                    author=message.author,
                    channel=message.channel,
                )

                return

        msg: discord.Message
        if message.reference:
            msg = await message.channel.send(
                tags_str, reference=message.reference, mention_author=False
            )
        else:
            msg = await message.channel.send(tags_str)

        await self.bot.messenger.publish(
            Events.on_set_deletable, msg=msg, author=message.author, timeout=60
        )

    async def get_tag_prefixes(self, bot: ClemBot, message: discord.Message) -> list[str] | None:
        tag_prefixes = []

        assert message.guild is not None

        # Check if bot is in BotOnly mode, if it is we cant get custom tag prefixes
        # so we have to fall back to self.default
        if not bot_secrets.secrets.bot_only:
            # noinspection PyBroadException
            try:
                # Try to grab the tag prefixes from the db, raise an error on failure
                # and bailout, we cant respond to anything at the moment
                tag_prefixes = await bot.custom_tag_prefix_route.get_custom_tag_prefixes(
                    message.guild.id, raise_on_error=True
                )
            except Exception:
                # if the api call fails for any reason then we bail out and return nothing
                # so as to not spam the servers with error messages on every message.
                # failing silently is preferable to that
                return None

        if len(tag_prefixes) == 0:
            tag_prefixes = [TAG_PREFIX_DEFAULT]

        return tag_prefixes

    async def load_service(self) -> None:
        pass
