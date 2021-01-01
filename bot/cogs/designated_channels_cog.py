import logging

import discord
import discord.ext.commands as commands

from bot.consts import Colors
import bot.extensions as ext
from bot.data.designated_channel_repository import DesignatedChannelRepository

log = logging.getLogger(__name__)

class DesignatedChannelsCog(commands.Cog):

    @ext.group(pass_context= True, invoke_without_command= True, aliases= ['channels'])
    @ext.long_help(
        'Designated channels are channels that you can set to for the bot to send a variety of info to ' 
        'You can register as many channels as youd like to any given category'
    )
    @ext.short_help('Designated channel configuration')
    @ext.example('channel')
    async def channel(self, ctx):
        """
        Sends a formatted embed of the possible designated channels and their listeners to 
        the context of the command
        """

        channel_repo = DesignatedChannelRepository()
        channels = await channel_repo.get_all_designated_channels()

        embed = discord.Embed(title= f'Designated Channels', color= Colors.ClemsonOrange)
        
        if channels is None:
            embed.add_field(name= 'No possible designated channels', value= '')
            await ctx.send(embed= embed)
            return

        for designated_id, name in channels:
            assigned_channels = []
            for channel_id in await channel_repo.get_guild_designated_channels(name, ctx.guild.id):
                assigned_channels.append(ctx.bot.get_channel(channel_id))

            if len(assigned_channels) != 0:
                embed_value = '\n'.join(c.mention for c in assigned_channels) 
            else:
                embed_value = 'No channel added'

            embed.add_field(
                name= f'#{designated_id} {name}', 
                value= embed_value,
                inline= False)
        
        await ctx.send(embed= embed)

    @channel.command(pass_context= True, aliases= ['register','set'])
    @commands.has_guild_permissions(administrator= True)
    @ext.long_help(
        'Adds a channel to a given designated channel listing, use the "channel" command to ' 
        'see a listing of all current and available designated channels'
    )
    @ext.short_help('Set a Designated channel')
    @ext.example('channel add user_join_log #some-channel')
    async def add(self, ctx, channel_type: str, channel: discord.TextChannel):

        channel_repo = DesignatedChannelRepository()

        if not await channel_repo.check_designated_channel(channel_type):
            await ctx.send(f'The requested designated channel `{channel_type}` does not exist')
            return

        if channel.id in await channel_repo.get_guild_designated_channels(channel_type, ctx.guild.id):
            await ctx.send(f'{channel.mention} already registered to `{channel_type}`')
            return
        
        await channel_repo.register_designated_channel(channel_type, channel)

        embed = discord.Embed(
            title= 'Designated Channel added', 
            color= Colors.ClemsonOrange)
        embed.add_field(
            name= channel_type,
            value=f'Successfully added {channel.mention} to `{channel_type}`')

        await ctx.send(embed= embed)

    @channel.command(pass_context= True, aliases= ['unregister'])
    @commands.has_guild_permissions(administrator= True)
    @ext.long_help(
        'Removes a channel from a given designated channel listing, use the "channel" command to ' 
        'see a listing of all current and available designated channels'
    )
    @ext.short_help('Removes a Designated channel listing')
    @ext.example('channel delete user_join_log #some-channel')
    async def delete(self, ctx, channel_type: str, channel: discord.TextChannel):
        """
        Command to delete a registered TextChannel from a designated channel 

        Args:
            channel_type (str): Designated channel to remove the textchannel from
            channel (discord.TextChannel): Channel to unregister
        """
        channel_repo = DesignatedChannelRepository()

        if not await channel_repo.check_designated_channel(channel_type):
            await ctx.send(f'The requested designated channel `{channel_type}` does not exist')
            return

        if channel.id not in await channel_repo.get_guild_designated_channels(channel_type, ctx.guild.id):
            await ctx.send(f'{channel.mention} is not registered to `{channel_type}`')
            return

        await channel_repo.remove_from_designated_channel(channel_type, channel.id)

        embed = discord.Embed(
            title= 'Designated Channel deleted', 
            color= Colors.ClemsonOrange)
        embed.add_field(
            name= channel_type,
            value=f'Successfully deleted {channel.mention} from `{channel_type}`')

        await ctx.send(embed= embed)
    

def setup(bot): 
    bot.add_cog(DesignatedChannelsCog(bot))
