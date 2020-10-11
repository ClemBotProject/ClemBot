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
from discord.ext.commands.errors import CheckFailure
from bot.messaging.events import Events

log = logging.getLogger(__name__)

MAX_TAG_CONTENT_SIZE = 1000
MAX_TAG_NAME_SIZE = 50
TAG_COMMAND_COOLDOWN = 30
TAG_CHUNK_SIZE = 25
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

    
    @commands.group(pass_context= True, invoke_without_command= True, aliases=['tags'])
    async def tag(self, ctx):
        tags = await TagRepository().get_all_server_tags(ctx.guild.id)


        embed = discord.Embed(title= f'Available Tags', color= Colors.ClemsonOrange)

        if tags:
            for chunk in self.chunk_list([role['name'] for role in tags], TAG_CHUNK_SIZE):
                embed.add_field(name= 'Available:', value= '\n'.join(chunk), inline= True)
        else:
            embed.add_field(name= 'Available:', value= 'No currently available tags')

        await ctx.send(embed= embed)

    @tag.command(aliases=['create', 'make'])
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

    @tag.command(aliases=['info'])
    async def about(self, ctx, name):
        
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
