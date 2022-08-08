import discord
import discord.ext.commands as commands

import bot.extensions as ext
from bot.clem_bot import ClemBot
from bot.consts import Claims, Colors, DesignatedChannels, OwnerDesignatedChannels
from bot.utils.logging_utils import get_logger

log = get_logger(__name__)


class DesignatedChannelsCog(commands.Cog):
    def __init__(self, bot: ClemBot) -> None:
        self.bot = bot

    @ext.group(case_insensitive=True, invoke_without_command=True, aliases=["channels"])
    @ext.required_claims(Claims.designated_channel_view)
    @ext.long_help(
        "Designated channels are channels that you can set to for the bot to send a variety of info to "
        "You can register as many channels as you'd like to any given category"
    )
    @ext.short_help("Designated channel configuration")
    @ext.example("channel")
    async def channel(self, ctx: ext.ClemBotCtx) -> None:
        """
        Sends a formatted embed of the possible designated channels and their listeners to
        the context of the command
        """
        embed = discord.Embed(title="Designated Channels", color=Colors.ClemsonOrange)

        if len(list(DesignatedChannels)) == 0:
            embed.add_field(name="No possible designated channels", value="")
            await ctx.send(embed=embed)
            return

        assert ctx.guild is not None

        designated_channels = (
            await self.bot.designated_channel_route.get_guild_all_designated_channels(ctx.guild.id)
        )

        for i, channel in enumerate(DesignatedChannels):
            assigned_channels = []
            for channel_id in designated_channels.get(channel.name, []):
                assigned_channels.append(ctx.bot.get_channel(channel_id))

            if len(assigned_channels) != 0:
                channels = []
                for ch in assigned_channels:
                    if ch is None or isinstance(ch, discord.abc.PrivateChannel):
                        continue
                    channels.append(ch)
                embed_value = "\n".join(c.mention for c in channels)
            else:
                embed_value = "No channel added"

            embed.add_field(name=f"#{i + 1} {channel.name}", value=embed_value, inline=False)

        await ctx.send(embed=embed)

    @channel.command(pass_context=True, aliases=["register", "set"])
    @ext.required_claims(Claims.designated_channel_modify)
    @ext.long_help(
        'Adds a channel to a given designated channel listing, use the "channel" command to '
        "see a listing of all current and available designated channels"
    )
    @ext.short_help("Set a Designated channel")
    @ext.example("channel add user_join_log #some-channel")
    async def add(
        self, ctx: ext.ClemBotCtx, channel_type: str, channel: discord.TextChannel
    ) -> None:

        if OwnerDesignatedChannels.has(channel_type):
            await ctx.send(
                f"""
                    The requested designated channel `{channel_type}` can only be managed by the owner of the bot instance
                    If you are the owner of the instance please reference owner_cog.py for more information
                    """
            )
            return

        if not DesignatedChannels.has(channel_type):
            await ctx.send(f"The requested designated channel `{channel_type}` does not exist")
            return

        assert ctx.guild is not None

        if channel.id in await self.bot.designated_channel_route.get_guild_designated_channel_ids(
            ctx.guild.id, channel_type
        ):
            await ctx.send(f"{channel.mention} already registered to `{channel_type}`")
            return

        await self.bot.designated_channel_route.register_channel(
            channel.id, channel_type, raise_on_error=True
        )

        embed = discord.Embed(title="Designated Channel added", color=Colors.ClemsonOrange)
        embed.add_field(
            name=channel_type, value=f"Successfully added {channel.mention} to `{channel_type}`"
        )

        await ctx.send(embed=embed)

    @channel.command(pass_context=True, aliases=["unregister"])
    @ext.required_claims(Claims.designated_channel_modify)
    @ext.long_help(
        'Removes a channel from a given designated channel listing, use the "channel" command to '
        "see a listing of all current and available designated channels"
    )
    @ext.short_help("Removes a Designated channel listing")
    @ext.example("channel delete user_join_log #some-channel")
    async def delete(
        self, ctx: ext.ClemBotCtx, channel_type: str, channel: discord.TextChannel
    ) -> None:
        """
        Command to delete a registered TextChannel from a designated channel

        Args:
            ctx (ext.ClemBotCtx): Context
            channel_type (str): Designated channel to remove the textchannel from
            channel (discord.TextChannel): Channel to unregister
        """
        if OwnerDesignatedChannels.has(channel_type):
            await ctx.send(
                f"""
                    The requested designated channel `{channel_type}` can only be managed by the owner of the bot instance
                    If you are the owner of the instance please reference owner_cog.py for more information
                    """
            )
            return

        if not DesignatedChannels.has(channel_type):
            await ctx.send(f"The requested designated channel `{channel_type}` does not exist")
            return

        assert ctx.guild is not None

        if (
            channel.id
            not in await self.bot.designated_channel_route.get_guild_designated_channel_ids(
                ctx.guild.id, channel_type
            )
        ):
            await ctx.send(f"{channel.mention} is not registered to `{channel_type}`")
            return

        await self.bot.designated_channel_route.delete_channel(
            channel.id, channel_type, raise_on_error=True
        )

        embed = discord.Embed(title="Designated Channel deleted", color=Colors.ClemsonOrange)
        embed.add_field(
            name=channel_type, value=f"Successfully deleted {channel.mention} from `{channel_type}`"
        )

        await ctx.send(embed=embed)


async def setup(bot: ClemBot) -> None:
    await bot.add_cog(DesignatedChannelsCog(bot))
