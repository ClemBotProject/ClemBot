import logging
from dataclasses import dataclass
from datetime import datetime

import discord
import discord.ext.commands as commands

import bot.extensions as ext
from bot.consts import Colors, Claims
from bot.data.claims_repository import ClaimsRepository
from bot.data.tag_repository import TagRepository
from bot.messaging.events import Events

log = logging.getLogger(__name__)

MAX_TAG_CONTENT_SIZE = 1000
MAX_TAG_NAME_SIZE = 20
TAG_CHUNK_SIZE = 15 * 3
MAX_NON_ADMIN_LINE_LENGTH = 10


@dataclass
class Tag:
    name: str
    content: str
    creation_date: str
    guild_id: int
    user_id: int


class TagCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @ext.group(invoke_without_command=True, aliases=['tags'], case_insensitive=True)
    @ext.long_help(
        'Either invokes a given tag or, if no tag is provided, '
        'Lists all the possible tags in the current server. '
        'tags can also be invoked with the inline command notation '
        '$<tag_name> anywhere in a message'
    )
    @ext.short_help('Supports custom tag functionality')
    @ext.example(('tag', 'tag mytag'))
    async def tag(self, ctx, tag=None):
        repo = TagRepository()

        if tag:
            if not await repo.check_tag_exists(tag, ctx.guild.id):
                embed = discord.Embed(title=f'Error: Tag "{tag}" does not exist in this server', color=Colors.Error)
                return await ctx.send(embed=embed)
            return await ctx.send(await repo.get_tag_content(tag, ctx.guild.id))

        tags = await repo.get_all_server_tags(ctx.guild.id)

        pages = []
        # check for if no tags exist in this server
        if not tags:
            embed = discord.Embed(title=f'Available Tags', color=Colors.ClemsonOrange)
            embed.add_field(name='Available:', value='No currently available tags')
            msg = await ctx.send(embed=embed)
            await self.bot.messenger.publish(Events.on_set_deletable, msg=msg, author=ctx.author)
            return

        # begin generating paginated columns
        # chunk the list of tags into groups of TAG_CHUNK_SIZE for each page
        for chunk in self.chunk_list([role['name'] for role in tags], TAG_CHUNK_SIZE):

            # we need to create the columns on the page so chunk the list again
            content = ''
            for col in self.chunk_list(chunk, 3):
                # the columns wont have the perfect number of elements every time, we need to append spaces if
                # the list entries is less then the number of columns
                while len(col) < 3:
                    col.append(' ')

                # Cocatenate the formatted column string to the page content string
                content += "{: <20} {: <20} {: <20}\n".format(*col)

            # Apped the content string to the list of pages to send to the paginator
            # Marked as a code block to ensure a monospaced font and even columns
            pages.append(f'```{content}```')

        # send the pages to the paginator service
        await self.bot.messenger.publish(Events.on_set_pageable_text,
                                         embed_name='Available Tags',
                                         field_title='Available:',
                                         pages=pages,
                                         author=ctx.author,
                                         channel=ctx.channel)

    @tag.command(aliases=['create', 'make'])
    @ext.required_claims(Claims.tag_add)
    @ext.long_help(
        'Creates a tag with a given name and value that can be invoked at any time in the future'
    )
    @ext.short_help('Creates a tag')
    @ext.example('tag add mytagname mytagcontnt')
    async def add(self, ctx, name: str, *, content: str):

        name = name.lower()

        is_admin = ctx.author.guild_permissions.administrator
        if len(content.split('\n')) > MAX_NON_ADMIN_LINE_LENGTH and not is_admin:
            embed = discord.Embed(title=f'Error: Tag line number exceeds  {MAX_NON_ADMIN_LINE_LENGTH} lines', color=Colors.Error)
            await ctx.send(embed=embed)
            return

        if len(content) > MAX_TAG_CONTENT_SIZE:
            embed = discord.Embed(title=f'Error: Tag content exceeds  {MAX_TAG_CONTENT_SIZE} characters', color=Colors.Error)
            await ctx.send(embed=embed)
            return

        if len(name) > MAX_TAG_NAME_SIZE:
            embed = discord.Embed(title=f'Error: Tag name exceeds {MAX_TAG_NAME_SIZE} characters', color=Colors.Error)
            await ctx.send(embed=embed)
            return

        content = discord.utils.escape_mentions(content)

        repo = TagRepository()
        if await repo.check_tag_exists(name, ctx.guild.id):
            embed = discord.Embed(title=f'Error: Tag "{name}" already exists in this server', color=Colors.Error)
            await ctx.send(embed=embed)
            return

        tag = Tag(name, content, datetime.utcnow(), ctx.guild.id, ctx.author.id)
        await TagRepository().insert_tag(tag)

        embed = discord.Embed(title=":white_check_mark: Tag successfully added", color=Colors.ClemsonOrange)
        embed.add_field(name="Name", value=name, inline=True)
        embed.add_field(name="Content", value=content, inline=True)
        await ctx.send(embed=embed)

    @tag.command(aliases=['remove', 'destroy'])
    @ext.required_claims(Claims.tag_delete)
    @ext.ignore_claims_pre_invoke()
    @ext.long_help(
        'Deletes a tag with a given name, this command can only be run by '
        'those with the tag_delete claim or the person who created the tag'
    )
    @ext.short_help('Deletes a tag')
    @ext.example('tag delete mytagname')
    async def delete(self, ctx: commands.Context, name):

        name=name.lower()

        tag_repo = TagRepository()
        claims_repo = ClaimsRepository()

        if not await tag_repo.check_tag_exists(name, ctx.guild.id):
            embed = discord.Embed(title=f'Error: tag {name} does not exist', color=Colors.Error)
            await ctx.send(embed=embed)
            return

        tag = await tag_repo.get_tag(name, ctx.guild.id)

        if tag['fk_UserId'] == ctx.author.id:
            await self._delete_tag(name, ctx)
            return

        claims = await claims_repo.fetch_all_claims_user(ctx.author)

        if ctx.command.claims_check(claims):
            await self._delete_tag(name, ctx)
            return

        error_str = f'Error: You do not have the tag_delete claim or you do not own this tag'
        embed = discord.Embed(title=error_str, color=Colors.Error)
        await ctx.send(embed=embed)

    @tag.command(aliases=['about'])
    @ext.long_help(
        'Provides info about a given tag including creation date, usage stats and tag owner'
    )
    @ext.short_help('Provides info about tag')
    @ext.example('tag info mytagname')
    async def info(self, ctx, name):

        name = name.lower()

        repo = TagRepository()

        if not await repo.check_tag_exists(name, ctx.guild.id):
            embed = discord.Embed(title=f'Error: Tag {name} does not exist', color=Colors.Error)
            await ctx.send(embed=embed)
            return

        tag = await repo.get_tag(name, ctx.guild.id)

        author = self.bot.get_user(tag['fk_UserId'])

        embed = discord.Embed(title='Tag Information:', color=Colors.ClemsonOrange)
        embed.add_field(name='Name ', value=tag['name'])
        embed.add_field(name='Content ', value=tag['content'])
        embed.add_field(name='Uses ', value=tag['useCount'], inline=False)
        fullNameGet = self.get_full_name(author)
        embed.add_field(name='Creation Date: ', value=tag['CreationDate'], inline=False)
        embed.set_footer(text=fullNameGet, icon_url=author.avatar_url)

        await ctx.send(embed=embed)

    async def _delete_tag(self, name, ctx):
        repo = TagRepository()
        content = await repo.get_tag_content(name, ctx.guild.id)

        await repo.delete_tag(name, ctx.guild.id)

        embed = discord.Embed(title=':white_check_mark: Tag successfully deleted', color=Colors.ClemsonOrange)
        embed.add_field(name='Name', value=name, inline=True)
        embed.add_field(name='Content', value=content, inline=True)
        await ctx.send(embed=embed)

    def get_full_name(self, author) -> str:
        return f'{author.name}#{author.discriminator}'

    def chunk_list(self, lst, n):
        """Yield successive n-sized chunks from lst."""
        for i in range(0, len(lst), n):
            yield lst[i:i + n]


def setup(bot):
    bot.add_cog(TagCog(bot))
