import asyncio
import logging
from collections import deque
import json

import discord
import discord.ext.commands as commands

import bot.extensions as ext
from bot.clem_bot import ClemBot
from bot.consts import Colors, OwnerDesignatedChannels, DesignatedChannels, Moderation

log = logging.getLogger(__name__)

MAX_MESSAGE_SIZE = 1900


class OwnerCog(commands.Cog):
    """ This is a cog for bot owner commands, things like log viewing and bot stats are shown here"""

    def __init__(self, bot):
        self.bot: ClemBot = bot

    @ext.group(hidden=True, case_insensitive=True)
    @commands.is_owner()
    async def owner(self, ctx):
        """For User by the bots owner to get errors and metrics"""
        pass

    @ext.group(invoke_without_command=True, hidden=True)
    @commands.is_owner()
    async def leave(self, ctx, id: int):
        server = self.bot.get_guild(id)
        await server.leave()

    @ext.group(invoke_without_command=True)
    @commands.is_owner()
    async def reload(self, ctx, id: int):
        guild = self.bot.get_guild(id)
        await ctx.send(f'reloading {guild.name} users')
        await self.bot.guild_route.update_guild_users(guild)

        await ctx.send(f'reloading {guild.name} roles')
        await self.bot.guild_route.update_guild_roles(guild)

        await ctx.send(f'reloading {guild.name} role user mappings')
        await self.bot.guild_route.update_guild_role_user_mappings(guild)

        await ctx.send(f'reloading {guild.name} channels')
        await self.bot.guild_route.update_guild_channels(guild)

        await ctx.send(f'reloading {guild.name} threads')
        await self.bot.guild_route.update_guild_threads(guild)

        await ctx.send(f'{guild.name} reloaded')

    @owner.group(invoke_without_command=True)
    @commands.is_owner()
    async def resetguilds(self, ctx, apply: bool = False):
        db_guilds = await self.bot.guild_route.get_all_guilds()
        db_guilds_ids = set(g['id'] for g in db_guilds)
        disc_guilds = set(g.id for g in self.bot.guilds)

        difference = db_guilds_ids - disc_guilds

        await ctx.send(f'Found the following guilds {difference}')

        if not apply:
            return

        for guild in difference:
            await ctx.send(f'Deleting Guild {guild} from database')
            await self.bot.guild_route.leave_guild(guild)

    @owner.group(invoke_without_command=True)
    @commands.is_owner()
    async def userupdatequeuestats(self, ctx, full_output: bool=False):
        queue = {k: str(v) if full_output else v.qsize() for k, v in self.bot.active_services['UserHandlingService'].user_update_queue.items()}
        await ctx.send(json.dumps(queue, indent=True))

    @owner.group(invoke_without_command=True)
    @commands.is_owner()
    async def queuestatus(self, ctx):
        stats = {}
        for k, v in self.bot.messenger._guild_event_queue.items():
            stats[k] = v.qsize()

        await ctx.send(json.dumps(stats, indent=2))

    @owner.group(invoke_without_command=True, aliases=['channels'])
    @commands.is_owner()
    async def channel(self, ctx):

        embed = discord.Embed(title=f'Owner Designated Channels', color=Colors.ClemsonOrange)

        if len(list(DesignatedChannels)) == 0:
            embed.add_field(name='No possible Owner designated channels', value='')
            await ctx.send(embed=embed)
            return

        designated_channels = await self.bot.designated_channel_route.get_guild_all_designated_channels(ctx.guild.id)

        for i, channel in enumerate(OwnerDesignatedChannels):
            assigned_channels = []
            for channel_id in designated_channels.get(channel.name, []):
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

        if DesignatedChannels.has(channel_type):
            await ctx.send(f'The requested designated channel `{channel_type}` is not an owner channel')
            return

        if channel.id in await self.bot.designated_channel_route.get_guild_designated_channel_ids(ctx.guild.id, channel_type):
            await ctx.send(f'{channel.mention} already registered to `{channel_type}`')
            return

        await self.bot.designated_channel_route.register_channel(channel.id, channel_type)

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
        if DesignatedChannels.has(channel_type):
            await ctx.send(f'The requested designated channel `{channel_type}` is not an owner channel')
            return

        if channel.id not in await self.bot.designated_channel_route.get_guild_designated_channel_ids(ctx.guild.id, channel_type):
            await ctx.send(f'{channel.mention} is not registered to `{channel_type}`')
            return

        await self.bot.designated_channel_route.delete_channel(channel.id, channel_type)

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

        """
        messages = await MessageRepository().get_message_count()
        embed.add_field(name='Messages', value=messages, inline=False)
        """

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
        exec_globals = {'asyncio': asyncio, 'bot': self.bot, 'code': code, 'ctx': ctx, 'loop': asyncio.get_running_loop(), 't': t, 'discord': discord}
        code = 'async def foobar():\n\t' + code + '\nt[0] = loop.create_task(foobar())'
        exec(code, exec_globals)
        await asyncio.gather(t[0])

    @eval_bot.command(aliases=['db'])
    @commands.is_owner()
    async def database(self, ctx, *, query):
        pass

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

    @owner.command()
    @commands.is_owner()
    async def updatemute(self, ctx):

        for guild in self.bot.guilds:
            mute_role = discord.utils.get(ctx.guild.roles, name=Moderation.mute_role_name)

            if not mute_role:
                continue

            await ctx.send(f'Updating guild {guild.name}')

            for channel in guild.channels:
                await channel.set_permissions(mute_role,
                                              speak=False,
                                              connect=False,
                                              stream=False,
                                              send_messages=False,
                                              send_messages_in_threads=False,
                                              create_public_threads=False,
                                              create_private_threads=False,
                                              send_tts_messages=False,
                                              add_reactions=False)

        await ctx.send('Done')

def setup(bot):
    bot.add_cog(OwnerCog(bot))
