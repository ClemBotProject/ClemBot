import time

import discord
import discord.ext.commands as commands
import requests

import bot.extensions as ext
from bot.clem_bot import ClemBot
from bot.consts import Colors


class PingPongCog(commands.Cog):
    def __init__(self, bot: ClemBot):
        self.bot = bot

    @ext.command(name="ping", aliases=["pong"])
    @commands.cooldown(1, 10, commands.BucketType.user)
    @ext.long_help(
        "Shows the latency between the bot's internal components and Discord as well as ClemBot's API if no arguments are provided. "
        "If a URL is provided, pings that URL."
    )
    @ext.short_help("shows bot latency / ping a URL")
    @ext.example("ping")
    async def ping(self, ctx: ext.ClemBotCtx, url: str = None) -> None:
        if not url:
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
        else:
            timeout = 3
            status = "success"
            start = time.perf_counter()
            try:
                requests.get(url, timeout=timeout)
            except requests.ConnectionError:
                status = "conn_error"
            except requests.ConnectTimeout:
                status = "conn_timeout"
            except (
                requests.exceptions.InvalidURL,
                requests.exceptions.MissingSchema,
                requests.exceptions.InvalidSchema,
            ):
                status = "invalid"
            elapsed = time.perf_counter() - start

            messages = {
                "success": f"The request to '{url}' returned successfully in {elapsed * 1000 : 1.2f}ms.",
                "conn_error": f"The server at '{url}' did not respond.",
                "conn_timeout": f"The server at '{url}' did not respond within {timeout} seconds.",
                "invalid": f"The URL '{url}' is invalid.",
            }

            embed = discord.Embed(
                color=Colors.ClemsonOrange if status == "success" else Colors.Error,
                title="Ping Result",
            )
            embed.add_field(name="Outcome", value=messages[status])
            embed.set_footer(text=str(ctx.author), icon_url=ctx.author.display_avatar.url)
            await ctx.send(embed=embed)


async def setup(bot: ClemBot) -> None:
    await bot.add_cog(PingPongCog(bot))
