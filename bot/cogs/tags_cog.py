from dataclasses import dataclass
import logging
from datetime import datetime

import discord
import discord.ext.commands as commands

from bot.data.tag_repository import TagRepository
from bot.consts import Colors
log = logging.getLogger(__name__)

MAX_TAG_CONTENT_SIZE = 1000
MAX_TAG_NAME_SIZE = 50
TAG_COMMAND_COOLDOWN = 30
TAG_CHUNK_SIZE = 25

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
    @commands.cooldown(1, TAG_COMMAND_COOLDOWN, commands.BucketType.user)
    async def add(self, ctx, name: str, *, content: str):

        name = name.lower()

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
            return
        
        await self._delete_tag(name, ctx)

    async def _delete_tag(self, name, ctx):
        await TagRepository().delete_tag(name, ctx.guild.id)
        embed=discord.Embed(title=':white_check_mark: Tag successfully deleted', color=Colors.ClemsonOrange)
        embed.add_field(name='Name', value=name, inline=True)
        await ctx.send(embed=embed)

    def get_full_name(self, author) -> str: 
        return f'{author.name}#{author.discriminator}' 

    def chunk_list(self, lst, n):
        """Yield successive n-sized chunks from lst."""
        for i in range(0, len(lst), n):
            yield lst[i:i + n]


def setup(bot): 
    bot.add_cog(TagCog(bot))
