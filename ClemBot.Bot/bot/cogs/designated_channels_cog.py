import logging

import discord
import discord.ext.commands as commands

import bot.extensions as ext
from bot.consts import Colors, DesignatedChannels, OwnerDesignatedChannels, Claims

log = logging.getLogger(__name__)


class DesignatedChannelsCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @ext.group(case_insensitive=True, invoke_without_command=True, aliases=['channels'])
    @ext.required_claims(Claims.designated_channel_view)
    @ext.long_help(
        "Designated channels are channels that you can set to for the bot to send a variety of info to "
        "You can register as many channels as you'd like to any given category"
    )
    @ext.short_help('Designated channel configuration')
    @ext.example('channel')
    async def channel(self, ctx):
        """
        Sends a formatted embed of the possible designated channels and their listeners to 
        the context of the command
        """
        embed = discord.Embed(title=f'Designated Channels', color=Colors.ClemsonOrange)

        if len(list(DesignatedChannels)) == 0:
            embed.add_field(name='No possible designated channels', value='')
            await ctx.send(embed=embed)
            return

        designated_channels = await self.bot.designated_channel_route.get_guild_all_designated_channels(ctx.guild.id)

        for i, channel in enumerate(DesignatedChannels):
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
    @ext.required_claims(Claims.designated_channel_modify)
    @ext.long_help(
        'Adds a channel to a given designated channel listing, use the "channel" command to '
        'see a listing of all current and available designated channels'
    )
    @ext.short_help('Set a Designated channel')
    @ext.example('channel add user_join_log #some-channel')
    async def add(self, ctx, channel_type: str, channel: discord.TextChannel):

        if OwnerDesignatedChannels.has(channel_type):
            await ctx.send(
                f"""
                    The requested designated channel `{channel_type}` can only be managed by the owner of the bot instance
                    If you are the owner of the instance please reference owner_cog.py for more information
                    """)
            return

        if not DesignatedChannels.has(channel_type):
            await ctx.send(f'The requested designated channel `{channel_type}` does not exist')
            return

        if channel.id in await self.bot.designated_channel_route.get_guild_designated_channel_ids(ctx.guild.id, channel_type):
            await ctx.send(f'{channel.mention} already registered to `{channel_type}`')
            return

        await self.bot.designated_channel_route.register_channel(channel.id, channel_type, raise_on_error=True)

        embed = discord.Embed(
            title='Designated Channel added',
            color=Colors.ClemsonOrange)
        embed.add_field(
            name=channel_type,
            value=f'Successfully added {channel.mention} to `{channel_type}`')

        await ctx.send(embed=embed)

    @channel.command(pass_context=True, aliases=['unregister'])
    @ext.required_claims(Claims.designated_channel_modify)
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
        if OwnerDesignatedChannels.has(channel_type):
            await ctx.send(
                f"""
                    The requested designated channel `{channel_type}` can only be managed by the owner of the bot instance
                    If you are the owner of the instance please reference owner_cog.py for more information
                    """)
            return

        if not DesignatedChannels.has(channel_type):
            await ctx.send(f'The requested designated channel `{channel_type}` does not exist')
            return

        if channel.id not in await self.bot.designated_channel_route.get_guild_designated_channel_ids(ctx.guild.id, channel_type):
            await ctx.send(f'{channel.mention} is not registered to `{channel_type}`')
            return

        await self.bot.designated_channel_route.delete_channel(channel.id, channel_type, raise_on_error=True)

        embed = discord.Embed(
            title='Designated Channel deleted',
            color=Colors.ClemsonOrange)
        embed.add_field(
            name=channel_type,
            value=f'Successfully deleted {channel.mention} from `{channel_type}`')

        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(DesignatedChannelsCog(bot))
