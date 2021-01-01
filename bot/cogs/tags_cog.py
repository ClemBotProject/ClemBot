import functools
import logging
import uuid
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

import discord
import discord.ext.commands as commands

from bot.consts import Colors
from bot.data.tag_repository import TagRepository
import bot.extensions as ext
from discord.ext.commands.errors import CheckFailure
from bot.messaging.events import Events

log = logging.getLogger(__name__)

MAX_TAG_CONTENT_SIZE = 1000
MAX_TAG_NAME_SIZE = 20
TAG_COMMAND_COOLDOWN = 30
TAG_CHUNK_SIZE = 15*3
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
        self._cd = commands.CooldownMapping.from_cooldown(1.0, TAG_COMMAND_COOLDOWN, commands.BucketType.user)

    
    @ext.group(invoke_without_command= True, aliases=['tags'])
    @ext.long_help(
        'Lists all the possible tags in the current server' 
        'tags are invoked with the command notation $<tag_name> anywhere in a message'
    )
    @ext.short_help('Supports custom tag functionality')
    @ext.example('tag')
    async def tag(self, ctx):
        tags = await TagRepository().get_all_server_tags(ctx.guild.id)

        pages = []
        #check for if no tags exist in this server
        if not tags:
            embed = discord.Embed(title= f'Available Tags', color= Colors.ClemsonOrange)
            embed.add_field(name= 'Available:', value= 'No currently available tags')
            msg = await ctx.send(embed= embed)
            await self.bot.messenger.publish(Events.on_set_deletable, msg=msg, author=ctx.author)
            return

        #begin generating paginated columns
        #chunk the list of tags into groups of TAG_CHUNK_SIZE for each page
        for chunk in self.chunk_list([role['name'] for role in tags], TAG_CHUNK_SIZE):

            #we need to create the columns on the page so chunk the list again
            content = ''
            for col in self.chunk_list(chunk, 3):
                #the columns wont have the perfect number of elements every time, we need to append spaces if
                #the list entries is less then the number of columns
                while len(col) <3:
                    col.append(' ')

                #Cocatenate the formatted column string to the page content string
                content += "{: <20} {: <20} {: <20}\n".format(*col)


            #Apped the content string to the list of pages to send to the paginator
            #Marked as a code block to ensure a monospaced font and even columns
            pages.append(f'```{content}```')

        #send the pages to the paginator service
        await self.bot.messenger.publish(Events.on_set_pageable_text,
                embed_name='Available Tags', 
                field_title='Available:',
                pages=pages, 
                author=ctx.author, 
                channel=ctx.channel)

    @tag.command(aliases=['create', 'make'])
    @ext.long_help(
        'Creates a tag with a given name and value that can be invoked at any time in the future' 
    )
    @ext.short_help('Creates a tag')
    @ext.example('tag add mytagname mytagcontnt')
    async def add(self, ctx, name: str, *, content: str):

        name = name.lower()

        is_admin = ctx.author.guild_permissions.administrator
        if len(content.split('\n')) > MAX_NON_ADMIN_LINE_LENGTH and not is_admin:
            embed = discord.Embed(title= f'Error: Tag line number exceeds  {MAX_NON_ADMIN_LINE_LENGTH} lines', color=Colors.Error)
            await ctx.send(embed=embed)
            return

        if len(content) > MAX_TAG_CONTENT_SIZE:
            embed = discord.Embed(title= f'Error: Tag content exceeds  {MAX_TAG_CONTENT_SIZE} characters', color=Colors.Error)
            await ctx.send(embed=embed)
            return

        if len(name) > MAX_TAG_NAME_SIZE:
            embed = discord.Embed(title= f'Error: Tag name exceeds {MAX_TAG_NAME_SIZE} characters', color=Colors.Error)
            await ctx.send(embed=embed)
            return 
        
        content = discord.utils.escape_mentions(content)

        repo = TagRepository()
        if await repo.check_tag_exists(name, ctx.guild.id):
            embed = discord.Embed(title= f'Error: Tag "{name}" already exists in this server', color=Colors.Error)
            await ctx.send(embed=embed)
            return
            
        tag = Tag(name, content, datetime.utcnow(), ctx.guild.id, ctx.author.id)
        await TagRepository().insert_tag(tag)

        embed=discord.Embed(title=":white_check_mark: Tag successfully added", color=Colors.ClemsonOrange)
        embed.add_field(name="Name", value=name, inline=True)
        embed.add_field(name="Content", value=content, inline=True)
        await ctx.send(embed=embed)


    @tag.command(aliases=['remove', 'destroy'])
    @ext.long_help(
        'Deletes a tag with a given name, this command can only be run by '
        'server staff or the person who created the tag'
    )
    @ext.short_help('Deletes a tag')
    @ext.example('tag delete mytagname mytagcontnt')
    async def delete(self, ctx, name):

        repo = TagRepository()

        if not await repo.check_tag_exists(name, ctx.guild.id):
            embed = discord.Embed(title= f'Error: Tag {name} does not exist', color=Colors.Error)
            await ctx.send(embed=embed)
            return

        tag = await repo.get_tag(name, ctx.guild.id)

        if ctx.author.guild_permissions.administrator:
            await self._delete_tag(name, ctx)
            return

        if tag['fk_UserId'] != ctx.author.id:
            embed = discord.Embed(title= f'Error: Tag {name} is not owned by {self.get_full_name(ctx.author)}',
                color=Colors.Error)
            await ctx.send(embed=embed)
            return
        
        await self._delete_tag(name, ctx)

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
            embed = discord.Embed(title= f'Error: Tag {name} does not exist', color=Colors.Error)
            await ctx.send(embed=embed)
            return

        tag = await repo.get_tag(name, ctx.guild.id)

        author = self.bot.get_user(tag['fk_UserId'])

        embed = discord.Embed(title='Tag Information:', color=Colors.ClemsonOrange)
        embed.add_field(name='Name ', value=tag['name'])
        embed.add_field(name='Content ', value=tag['content'])
        fullNameGet = self.get_full_name(author)
        embed.set_footer(text=fullNameGet, icon_url=author.avatar_url)
        embed.add_field(name='Creation Date: ', value=tag['CreationDate'], inline=False)

        await ctx.send(embed=embed)

    async def _delete_tag(self, name, ctx):
        await TagRepository().delete_tag(name, ctx.guild.id)
        embed=discord.Embed(title=':white_check_mark: Tag successfully deleted', color=Colors.ClemsonOrange)
        embed.add_field(name='Name', value=name, inline=True)
        await ctx.send(embed=embed)

    async def cog_check(self, ctx):
        bucket = self._cd.get_bucket(ctx.message)
        retry_after = bucket.update_rate_limit()
        if retry_after and ctx.message.author.guild_permissions.administrator:
            return True
        elif retry_after:
            embed = discord.Embed(title='Error: Command on cooldown', color=Colors.Error)
            embed.add_field(name='Cooldown remaining', value=f'{round(retry_after, 2)} seconds remaining')
            embed.set_footer(text=self.get_full_name(ctx.author), icon_url=ctx.author.avatar_url)
            await ctx.send(embed=embed)
            return False
        return True
    
    async def cog_command_error(self, ctx, e):
        if isinstance(e, CheckFailure):
            pass
        else:
            embed = discord.Embed(title="ERROR: Command exception", color=Colors.Error)
            embed.add_field(name='Exception:', value= e)
            embed.set_footer(text=self.get_full_name(ctx.author), icon_url=ctx.author.avatar_url)
            msg = await ctx.channel.send(embed= embed)
            await self.bot.messenger.publish(Events.on_set_deletable, msg=msg, author=ctx.author)
            await self.bot.global_error_handler(e)


    def get_full_name(self, author) -> str: 
        return f'{author.name}#{author.discriminator}' 

    def chunk_list(self, lst, n):
        """Yield successive n-sized chunks from lst."""
        for i in range(0, len(lst), n):
            yield lst[i:i + n]


def setup(bot): 
    bot.add_cog(TagCog(bot))
