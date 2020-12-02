import json
import logging
from collections import deque

import aiosqlite
import discord
import discord.ext.commands as commands

from bot.bot_secrets import BotSecrets
from bot.consts import Colors, DiscordLimits
from bot.data.base_repository import BaseRepository
from bot.data.guild_repository import GuildRepository
from bot.data.message_repository import MessageRepository
from bot.data.user_repository import UserRepository

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
        server = self.bot.get_server(id)
        await self.bot.leave_server(server)

    @owner.group(invoke_without_command=True)
    @commands.is_owner()
    async def count(self, ctx):
        embed = discord.Embed(title='Available metrics', color=Colors.ClemsonOrange)
        embed.add_field(name='Commands', value='Guilds\nMessages\nUsers')
        await ctx.send(embed=embed)

    @owner.group(invoke_without_command=True, aliases=['db'])
    @commands.is_owner()
    async def database(self, ctx):
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
            chunks = [logs[i:i+MAX_MESSAGE_SIZE] for i in range(0, len(logs), MAX_MESSAGE_SIZE)]
            for c in chunks:
                await ctx.send(f'```{c}```')

    @database.command()
    @commands.is_owner()
    async def eval(self, ctx, *, query):
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
    async def messages(self, ctx, guild_id: int=None):
        count = await MessageRepository().get_message_count(guild_id)
        embed = discord.Embed(title='Current message count', color=Colors.ClemsonOrange)
        embed.add_field(name=f'Guild: {guild_id}' if guild_id else 'Global', value=count)
        await ctx.send(embed=embed)
    
    @count.command()
    @commands.is_owner()
    async def guilds(self, ctx):
        count = await GuildRepository().get_guild_count()
        embed = discord.Embed(title='Current guild count', color=Colors.ClemsonOrange)
        embed.add_field(name='Global', value=count)
        await ctx.send(embed=embed)

    @count.command()
    @commands.is_owner()
    async def users(self, ctx, guild_id: int=None):
        count = await UserRepository().get_user_count(guild_id)
        embed = discord.Embed(title='Current user count', color=Colors.ClemsonOrange)
        embed.add_field(name=f'Guild: {guild_id}' if guild_id else 'Global', value=count)
        await ctx.send(embed=embed)


def setup(bot): 
    bot.add_cog(OwnerCog(bot))
