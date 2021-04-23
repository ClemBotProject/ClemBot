import asyncio
import json
import logging
from collections import deque

import aiosqlite
import discord
import discord.ext.commands as commands

from bot.bot_secrets import BotSecrets
from bot.consts import Colors, DiscordLimits, OwnerDesignatedChannels, DesignatedChannels
from bot.data.base_repository import BaseRepository
from bot.data.designated_channel_repository import DesignatedChannelRepository
from bot.data.message_repository import MessageRepository

log = logging.getLogger(__name__)

MAX_MESSAGE_SIZE = 1900


class OwnerCog(commands.Cog):
    """ This is a cog for bot owner commands, things like log viewing and bot stats are shown here"""

    def __init__(self, bot):
        self.bot = bot

    @commands.group(hidden=True, invoke_without_command=True, case_insensitive=True)
    @commands.is_owner()
    async def owner(self, ctx):
        """For User by the bots owner to get errors and metrics"""
        pass

    @owner.group(invoke_without_command=True)
    @commands.is_owner()
    async def leave(self, ctx, id: int):
        server = self.bot.get_guild(id)
        await server.leave()

    @owner.group(invoke_without_command=True, aliases=['channels'])
    @commands.is_owner()
    async def channel(self, ctx):
        channel_repo = DesignatedChannelRepository()

        embed = discord.Embed(title=f'Designated Channels', color=Colors.ClemsonOrange)

        for i, channel in enumerate(OwnerDesignatedChannels):
            assigned_channels = []
            for channel_id in await channel_repo.get_guild_designated_channels(channel.name, ctx.guild.id):
                assigned_channels.append(ctx.bot.get_channel(channel_id))

            if len(assigned_channels) != 0:
                embed_value = '\n'.join(c.mention for c in assigned_channels)
            else:
                embed_value = 'No channel added'

            embed.add_field(
                name=f'#{i + 1} {channel.name}',
                value=embed_value,
                inline=False)

        await ctx.send(embed=embed)

    @channel.command(pass_context=True, aliases=['register', 'set'])
    @commands.is_owner()
    async def add(self, ctx, channel_type: str, channel: discord.TextChannel):
        """
        Command to add a registered TextChannel too an owner designated channel 

        Args:
            channel_type (str): Designated channel to add the textchannel too
            channel (discord.TextChannel): Channel to add
        """

        channel_repo = DesignatedChannelRepository()

        if DesignatedChannels.has(channel_type):
            await ctx.send(f'The requested designated channel `{channel_type}` is not an owner channel')
            return

        if channel.id in await channel_repo.get_guild_designated_channels(channel_type, ctx.guild.id):
            await ctx.send(f'{channel.mention} already registered to `{channel_type}`')
            return

        await channel_repo.register_designated_channel(channel_type, channel)

        embed = discord.Embed(
            title='Owner Designated Channel added',
            color=Colors.ClemsonOrange)
        embed.add_field(
            name=channel_type,
            value=f'Successfully added {channel.mention} to `{channel_type}`')

        await ctx.send(embed=embed)

    @channel.command(pass_context=True, aliases=['unregister'])
    @commands.is_owner()
    async def delete(self, ctx, channel_type: str, channel: discord.TextChannel):
        """
        Command to delete a registered TextChannel from an owner designated channel 

        Args:
            channel_type (str): Designated channel to remove the textchannel from
            channel (discord.TextChannel): Channel to unregister
        """
        channel_repo = DesignatedChannelRepository()

        if DesignatedChannels.has(channel_type):
            await ctx.send(f'The requested designated channel `{channel_type}` is not an owner channel')
            return

        if channel.id not in await channel_repo.get_guild_designated_channels(channel_type, ctx.guild.id):
            await ctx.send(f'{channel.mention} is not registered to `{channel_type}`')
            return

        await channel_repo.remove_from_designated_channel(channel_type, channel.id)

        embed = discord.Embed(
            title='Owner Designated Channel deleted',
            color=Colors.ClemsonOrange)
        embed.add_field(
            name=channel_type,
            value=f'Successfully deleted {channel.mention} from `{channel_type}`')

        await ctx.send(embed=embed)

    @owner.group(invoke_without_command=True)
    @commands.is_owner()
    async def count(self, ctx):
        msg = await ctx.send('Querying global bot metrics (this might take a while)')

        embed = discord.Embed(title='Available metrics', color=Colors.ClemsonOrange)
        embed.add_field(name='Guilds', value=len(self.bot.guilds), inline=False)

        embed.add_field(name='Users', value=sum(len(i.members) for i in self.bot.guilds), inline=False)

        messages = await MessageRepository().get_message_count()
        embed.add_field(name='Messages', value=messages, inline=False)

        await msg.delete()
        await ctx.send(embed=embed)

    @owner.group(invoke_without_command=True, aliases=['eval'])
    @commands.is_owner()
    async def eval_bot(self, ctx):
        pass

    @owner.group(invoke_without_command=True)
    @commands.is_owner()
    async def log(self, ctx):
        pass

    @log.command()
    @commands.is_owner()
    async def get(self, ctx, lines: int):
        log_name = log.parent.handlers[0].baseFilename
        with open(log_name, 'r') as f:
            logs = "".join(deque(f, lines))
            chunks = [logs[i:i + MAX_MESSAGE_SIZE] for i in range(0, len(logs), MAX_MESSAGE_SIZE)]
            for c in chunks:
                await ctx.send(f'```{c}```')

    @eval_bot.command()
    @commands.is_owner()
    async def bot(self, ctx, *, code):
        code = code.replace('```python', '')
        code = code.replace('```py', '')
        code = code.replace('`', '')
        code = code.replace('\n', '\n\t')
        t = [None]
        exec_globals = {'asyncio': asyncio, 'bot': self.bot, 'code': code, 'ctx': ctx, 'loop': asyncio.get_running_loop(), 't': t}
        code = 'async def foobar():\n\t' + code + '\nt[0] = loop.create_task(foobar())'
        exec(code, exec_globals)
        await asyncio.gather(t[0])

    @eval_bot.command(aliases=['db'])
    @commands.is_owner()
    async def database(self, ctx, *, query):
        """Runs arbitrary sql queries on the db in readonly mode and returns the results"""

        database_name = BotSecrets.get_instance().database_name
        db_path = f'database/{database_name}'
        connect_mode = 'ro'
        json_params = {
            'indent': 2,
            'separators': (',', ': ')
        }

        async with aiosqlite.connect(f'file:{db_path}?mode={connect_mode}', uri=True) as db:
            async with db.execute(query) as c:
                result = await BaseRepository().fetcthall_as_dict(c)

        json_res = json.dumps(result, **json_params)

        if len(json_res) > DiscordLimits.MessageLength:
            await ctx.send('Query result greater then discord message length limit')
            return

        await ctx.send(f'```{json_res}```')

    @count.command()
    @commands.is_owner()
    async def messages(self, ctx, guild_id: int = None):
        count = await MessageRepository().get_message_count(guild_id)
        embed = discord.Embed(title='Current message count', color=Colors.ClemsonOrange)
        embed.add_field(name=f'Guild: {guild_id}' if guild_id else 'Global', value=count)
        await ctx.send(embed=embed)

    @count.command()
    @commands.is_owner()
    async def guilds(self, ctx):
        count = len(self.bot.guilds)

        embed = discord.Embed(title='Current guild count', color=Colors.ClemsonOrange)
        embed.add_field(name='Global', value=count)

        await ctx.send(embed=embed)

    @count.command()
    @commands.is_owner()
    async def users(self, ctx, guild_id: int = None):
        count = sum(len(i.members) for i in self.bot.guilds)

        embed = discord.Embed(title='Current user count', color=Colors.ClemsonOrange)
        embed.add_field(name=f'Guild: {guild_id}' if guild_id else 'Global', value=count)

        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(OwnerCog(bot))
