import logging
import discord
import typing as t
import bot.extensions as ext
import discord.ext.commands as commands

from bot.api.tag_route import Tag
from bot.consts import Colors, Claims
from bot.messaging.events import Events

log = logging.getLogger(__name__)

MAX_TAG_CONTENT_SIZE = 1000
MAX_TAG_NAME_SIZE = 20
TAG_CHUNK_SIZE = 15 * 3
MAX_NON_ADMIN_LINE_LENGTH = 10


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
    async def tag(self, ctx, tag_name=None):

        if tag_name:
            tag = await self.bot.tag_route.get_tag(ctx.guild.id, tag_name)
            if not tag:
                embed = discord.Embed(title=f'Error: Tag "{tag_name}" does not exist in this server', color=Colors.Error)
                return await ctx.send(embed=embed)
            await self.bot.tag_route.add_tag_use(ctx.guild.id, tag_name, ctx.channel.id, ctx.author.id)
            return await ctx.send(tag.content)

        tags = await self.bot.tag_route.get_guilds_tags(ctx.guild.id)

        # check for if no tags exist in this server
        if not tags:
            embed = discord.Embed(title=f'Available Tags', color=Colors.ClemsonOrange)
            embed.add_field(name='Available:', value='No currently available tags')
            msg = await ctx.send(embed=embed)
            await self.bot.messenger.publish(Events.on_set_deletable, msg=msg, author=ctx.author)
            return

        # begin generating paginated columns
        # chunk the list of tags into groups of TAG_CHUNK_SIZE for each page
        pages = self.chunked_pages([role.name for role in tags], TAG_CHUNK_SIZE)

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
    @ext.example('tag add mytagname mytagcontent')
    async def add(self, ctx, name: str, *, content: str):
        is_admin = ctx.author.guild_permissions.administrator
        if len(content.split('\n')) > MAX_NON_ADMIN_LINE_LENGTH and not is_admin:
            embed = discord.Embed(title=f'Error: Tag line number exceeds {MAX_NON_ADMIN_LINE_LENGTH} lines', color=Colors.Error)
            await ctx.send(embed=embed)
            return

        if len(content) > MAX_TAG_CONTENT_SIZE:
            embed = discord.Embed(title=f'Error: Tag content exceeds {MAX_TAG_CONTENT_SIZE} characters', color=Colors.Error)
            await ctx.send(embed=embed)
            return

        if len(name) > MAX_TAG_NAME_SIZE:
            embed = discord.Embed(title=f'Error: Tag name exceeds {MAX_TAG_NAME_SIZE} characters', color=Colors.Error)
            await ctx.send(embed=embed)
            return

        content = discord.utils.escape_mentions(content)

        if await self.bot.tag_route.get_tag(ctx.guild.id, name):
            embed = discord.Embed(title=f'Error: Tag "{name}" already exists in this server', color=Colors.Error)
            await ctx.send(embed=embed)
            return

        await self.bot.tag_route.create_tag(name, content, ctx.guild.id, ctx.author.id, raise_on_error=True)

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
        if not (tag := await self._check_tag_exists(ctx, name)):
            return

        if tag.user_id == ctx.author.id:
            await self._delete_tag(name, ctx)
            return

        claims = await self.bot.claim_route.get_claims_user(ctx.author)

        if ctx.command.claims_check(claims):
            await self._delete_tag(name, ctx)
            return

        embed = discord.Embed(title='Error', color=Colors.Error,
                              description='You do not have the `tag_delete` claim or you do not own this tag.')
        embed.set_footer(text=self.get_full_name(ctx.author), icon_url=ctx.author.avatar_url)
        await ctx.send(embed=embed)

    @tag.command(aliases=['about'])
    @ext.long_help(
        'Provides info about a given tag including creation date, usage stats and tag owner'
    )
    @ext.short_help('Provides info about tag')
    @ext.example('tag info mytagname')
    async def info(self, ctx, name: str):
        if not (tag := await self._check_tag_exists(ctx, name)):
            return
        author = ctx.guild.get_member(tag.user_id)
        description = ':warning: This tag is unclaimed.' if author is None else ''
        embed = discord.Embed(title='Tag Information', color=Colors.ClemsonOrange, description=description)
        embed.add_field(name='Name ', value=tag.name)
        embed.add_field(name='Content ', value=tag.content, inline=False)
        embed.add_field(name='Uses ', value=f'{tag.use_count}', inline=True)
        embed.add_field(name='Creation Date', value=tag.creation_date, inline=True)
        if author is not None:
            embed.set_footer(text=self.get_full_name(author), icon_url=author.avatar_url)
        await ctx.send(embed=embed)

    @tag.command()
    @ext.required_claims(Claims.tag_add)
    @ext.short_help('Claims a tag')
    @ext.long_help('Claims a tag with the given name as your own')
    @ext.example('tag claim mytagname')
    async def claim(self, ctx, name: str):
        if not (tag := await self._check_tag_exists(ctx, name)):
            return
        author = ctx.guild.get_member(tag.user_id)
        if author is not None:
            embed = discord.Embed(title=f'Error: Tag {name} is already claimed', color=Colors.Error)
            embed.set_footer(text=self.get_full_name(author), icon_url=author.avatar_url)
            await ctx.send(embed=embed)
            return
        await self.bot.tag_route.edit_tag(ctx.guild.id, tag.name, tag.content, ctx.message.author.id)
        embed = discord.Embed(title=f':white_check_mark: Tag successfully claimed', color=Colors.ClemsonOrange)
        embed.add_field(name='Name', value=tag.name, inline=True)
        embed.add_field(name='Content', value=tag.content, inline=True)
        await ctx.send(embed=embed)

    @tag.command(aliases=['unowned'])
    @ext.short_help('Lists all unclaimed tags')
    @ext.long_help('Gets a list of all unowned tags available to be claimed')
    @ext.example(['tag unclaimed', 'tag unowned'])
    async def unclaimed(self, ctx):
        guild_tags = await self.bot.tag_route.get_guilds_tags(ctx.guild.id)
        unclaimed_tags = list[str]()
        for tag in guild_tags[0::]:
            if ctx.guild.get_member(tag.user_id) is None:
                unclaimed_tags.append(tag.name)

        author = ctx.author
        if len(unclaimed_tags) == 0:
            embed = discord.Embed(title='No Unclaimed Tags', color=Colors.Error,
                                  description='There are no unclaimed tags in this guild.')
            embed.set_footer(text=self.get_full_name(author), icon_url=author.avatar_url)
            await ctx.send(embed=embed)
            return

        # chunk the unclaimed tags into pages
        pages = self.chunked_pages(unclaimed_tags, TAG_CHUNK_SIZE)

        # send the pages to the paginator service
        await self.bot.messenger.publish(Events.on_set_pageable_text,
                                         embed_name='Unclaimed Tags',
                                         field_title='Unclaimed:',
                                         pages=pages,
                                         author=ctx.author,
                                         channel=ctx.channel)

    @tag.command(aliases=['give'])
    @ext.required_claims(Claims.tag_add)
    @ext.short_help('Gives your tag to someone else.')
    @ext.long_help('Transfers the tag to the given user.')
    @ext.example(['tag transfer tagname @user', 'tag give tagname @user'])
    async def transfer(self, ctx, name: str, user: discord.User):
        if not (tag := await self._check_tag_exists(ctx, name)):
            return
        author = ctx.author
        if user.id == author.id and tag.user_id == user.id:
            embed = discord.Embed(title='Error', color=Colors.Error,
                                  description='Why are you giving a tag you own to yourself...?')
            embed.set_footer(text=self.get_full_name(author), icon_url=author.avatar_url)
            await ctx.send(embed=embed)
            return
        is_admin = author.guild_permissions.administrator
        if author.id != tag.user_id and not is_admin:
            embed = discord.Embed(title='Error', color=Colors.Error,
                                  description=f"You do not own the tag '{tag.name}'.")
            embed.set_footer(text=self.get_full_name(author), icon_url=author.avatar_url)
            await ctx.send(embed=embed)
            return
        await self.bot.tag_route.edit_tag(ctx.guild.id, name, tag.content, user.id)
        embed = discord.Embed(title=':white_check_mark: Tag Transferred', color=Colors.ClemsonOrange)
        original_owner = ctx.guild.get_member(tag.user_id)
        embed.add_field(name='From', value=f'{original_owner.mention} :arrow_right:')
        embed.add_field(name='To', value=user.mention)
        embed.add_field(name='Name', value=tag.name, inline=False)
        embed.add_field(name='Content', value=tag.content, inline=False)
        await ctx.send(embed=embed)

    async def _delete_tag(self, name, ctx):
        content = await self.bot.tag_route.get_tag_content(ctx.guild.id, name)

        await self.bot.tag_route.delete_tag(ctx.guild.id, name, raise_on_error=True)

        embed = discord.Embed(title=':white_check_mark: Tag successfully deleted', color=Colors.ClemsonOrange)
        embed.add_field(name='Name', value=name, inline=True)
        embed.add_field(name='Content', value=content, inline=True)
        await ctx.send(embed=embed)

    async def _check_tag_exists(self, ctx, name: str) -> t.Optional[Tag]:
        """
        Checks if the given tag exists.
        If so, returns the tag.
        If not, sends message and returns nothing.
        """
        tag = await self.bot.tag_route.get_tag(ctx.guild.id, name)
        if not tag:
            embed = discord.Embed(title='Error', color=Colors.Error,
                                  description=f"Requested tag '{name}' does not exist.")
            embed.set_footer(text=self.get_full_name(ctx.author), icon_url=ctx.author.avatar_url)
            await ctx.send(embed=embed)
            return None
        return tag

    async def _check_tag_owner(self, ctx, tag: Tag) -> t.Optional[discord.User]:
        pass

    def get_full_name(self, author) -> str:
        return f'{author.name}#{author.discriminator}'

    def chunk_list(self, lst, n):
        """Yield successive n-sized chunks from lst."""
        for i in range(0, len(lst), n):
            yield lst[i:i + n]

    def chunked_pages(self, tags_list: list, n: int):
        """Chunks the given list into a markdown-ed list of n-sized items (row * col)"""
        pages = []
        for chunk in self.chunk_list(tags_list, n):
            content = ''
            for col in self.chunk_list(chunk, 3):
                # the columns wont have the perfect number of elements every time, we need to append spaces if
                # the list entries is less then the number of columns
                while len(col) < 3:
                    col.append(' ')

                # Concatenate the formatted column string to the page content string
                content += "{: <20} {: <20} {: <20}\n".format(*col)

            # Append the content string to the list of pages to send to the paginator
            # Marked as a code block to ensure a monospaced font and even columns
            pages.append(f'```{content}```')
        return pages


def setup(bot):
    bot.add_cog(TagCog(bot))
