import aiohttp
import discord
import discord.ext.commands as commands

import bot.extensions as ext
from bot.clem_bot import ClemBot
from bot.consts import Claims, Colors
from bot.utils.logging_utils import get_logger

log = get_logger(__name__)


class EmoteCog(commands.Cog):
    def __init__(self, bot: ClemBot) -> None:
        self.bot = bot

    @ext.group(hidden=True, aliases=["emoji"])
    async def emote(self, ctx: ext.ClemBotCtx) -> None:
        pass

    @emote.command()
    @ext.required_claims(Claims.emote_add)
    async def add(self, ctx: ext.ClemBotCtx, emote: discord.PartialEmoji, name: str) -> None:
        slots = self._get_emote_count(ctx, emote.animated)
        if ctx.guild.emoji_limit - slots == 0:
            embed = discord.Embed(title="Error", color=Colors.Error)
            embed.description = (
                "**Could not add emoji:** all emoji slots for this server are filled."
            )
            embed.set_footer(text=str(ctx.author), icon_url=ctx.author.display_avatar.url)
            await ctx.send(embed=embed)
            return
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"https://cdn.discordapp.com/emojis/{emote.id}.{'gif' if emote.animated else 'png'}?v=1"
            ) as resp:
                image = await resp.read()

        assert ctx.guild is not None

        emoji = await ctx.guild.create_custom_emoji(name=name, image=image)

        log.info(f"Emote added in guild: {ctx.guild.id}, name: {emoji.name}, by: {ctx.author.id}")

        embed = discord.Embed(title="Emoji Created :white_check_mark:", color=Colors.ClemsonOrange)
        embed.add_field(name="Name:", value=f"```{emoji.name}```")
        embed.set_thumbnail(url=emoji.url)
        embed.set_footer(
            text=f"Created By: {str(ctx.author)}", icon_url=ctx.author.display_avatar.url
        )
        await ctx.send(embed=embed)

    def _get_emote_count(self, ctx: ext.ClemBotCtx, animated: bool) -> int:
        emotes = 0
        for emote in ctx.guild.emojis:
            if emote.animated == animated:
                emotes += 1
        return emotes


async def setup(bot: ClemBot) -> None:
    await bot.add_cog(EmoteCog(bot))
