import asyncio.exceptions
import time
from typing import Optional

import aiohttp
import discord
import discord.ext.commands as commands

import bot.extensions as ext
from bot.clem_bot import ClemBot
from bot.consts import Colors


class PingPongCog(commands.Cog):
    def __init__(self, bot: ClemBot):
        self.bot = bot

    async def handle_bot_ping(self, ctx: ext.ClemBotCtx) -> None:
        start = time.perf_counter()
        await self.bot.health_check_route.ping()
        clembot_api_latency = time.perf_counter() - start

        embed = discord.Embed(color=Colors.ClemsonOrange, title="ClemBot Latency :stopwatch:")
        embed.add_field(name="Discord WebSocket", value=f"{self.bot.latency * 1000 : 1.2f}ms")
        embed.add_field(name="Discord HTTP", value=":infinity:ms")
        embed.add_field(name="ClemBot API", value=f"{clembot_api_latency * 1000 : 1.2f}ms")
        embed.set_footer(text=str(ctx.author), icon_url=ctx.author.display_avatar.url)

        start = time.perf_counter()

        sent_message = await ctx.send(embed=embed)

        discord_http_latency = (time.perf_counter() - start) * 1000

        embed.remove_field(1)
        embed.insert_field_at(1, name="Discord HTTP", value=f"{discord_http_latency : 1.2f}ms")

        await sent_message.edit(embed=embed)

    async def handle_external_ping(self, ctx: ext.ClemBotCtx, url: str) -> None:
        timeout = 3
        start = time.perf_counter()
        color = Colors.Error
        message = None
        try:
            async with aiohttp.ClientSession() as session:
                await session.get(url, timeout=timeout)
                color = Colors.ClemsonOrange
        except asyncio.exceptions.TimeoutError:
            message = f"The server at '{url}' did not respond within {timeout} seconds."
        except aiohttp.InvalidURL:
            message = f"The URL '{url}' is invalid."
        elapsed = time.perf_counter() - start
        if not message:
            message = f"The request to '{url}' returned successfully in {elapsed * 1000 : 1.2f}ms."

        embed = discord.Embed(
            color=color,
            title="Ping Result",
        )
        embed.add_field(name="Outcome", value=message)
        embed.set_footer(text=str(ctx.author), icon_url=ctx.author.display_avatar.url)
        await ctx.send(embed=embed)

    @ext.command(name="ping", aliases=["pong"])
    @commands.cooldown(1, 10, commands.BucketType.user)
    @ext.long_help(
        "Shows the latency between the bot's internal components and Discord as well as ClemBot's API if no arguments are provided. "
        "If a URL is provided, pings that URL."
    )
    @ext.short_help("shows bot latency / ping a URL")
    @ext.example("ping")
    async def ping(self, ctx: ext.ClemBotCtx, url: Optional[str] = None) -> None:
        if not url:
            await self.handle_bot_ping(ctx)
        else:
            await self.handle_external_ping(ctx, url)


async def setup(bot: ClemBot) -> None:
    await bot.add_cog(PingPongCog(bot))
