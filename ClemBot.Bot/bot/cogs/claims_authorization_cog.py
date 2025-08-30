import typing as t

import discord
import discord.ext.commands as commands

import bot.extensions as ext
from bot.clem_bot import ClemBot
from bot.consts import Claims, Colors
from bot.utils.converters import ClaimsConverter


class ClaimsAuthorizationCog(commands.Cog):
    def __init__(self, bot: ClemBot) -> None:
        self.bot = bot

    @ext.group(invoke_without_command=True, aliases=["auth", "claim"])
    @ext.required_claims(Claims.claims_view)
    @ext.long_help(
        "Claims represent privileges within the bot. "
        "Each claim gives access to different functionality and can be added to as many "
        "roles as desired"
    )
    @ext.short_help("Claims authorization setup")
    @ext.example(("claims", "claims @some_role", "claims @some_user"))
    @ext.docs("Claims", "claims")
    async def claims(
        self, ctx: ext.ClemBotCtx, listing: t.Union[discord.Role, discord.Member]
    ) -> None:
        assert isinstance(ctx.author, discord.Member)

        listing = listing or ctx.author

        if isinstance(listing, discord.Role):
            await self._send_role_claims(ctx, listing)
        elif isinstance(listing, discord.Member):
            await self._send_user_claims(ctx, listing)

    async def _send_role_claims(self, ctx: ext.ClemBotCtx, role: discord.Role) -> None:
        claims = await self.bot.claim_route.get_claims_role(role.id)

        embed = self._build_claims_embed(ctx, claims, role)
        await ctx.send(embed=embed)

    async def _send_user_claims(self, ctx: ext.ClemBotCtx, user: discord.Member) -> None:
        claims = await self.bot.claim_route.get_claims_user(user)

        embed = self._build_claims_embed(ctx, claims, user)
        await ctx.send(embed=embed)

    def _build_claims_embed(
        self,
        ctx: ext.ClemBotCtx,
        claims: list[Claims],
        subject: discord.Role | discord.Member,
    ) -> discord.Embed:

        claims_str = "\n".join(sorted([c.name for c in claims])) if claims else "No current claims"

        embed = discord.Embed(
            title="Current Valid Claims",
            color=Colors.ClemsonOrange,
            description=f"For: {subject.mention}\n```\n{claims_str}```",
        )
        embed.set_footer(text=str(ctx.author), icon_url=ctx.author.display_avatar.url)
        return embed

    @claims.command(aliases=["set"])
    @ext.required_claims(Claims.claims_modify)
    @ext.long_help(
        "Adds a claim to a given role. "
        "Who ever has that role will have access to that functionality"
    )
    @ext.short_help("Add claims to a given role")
    @ext.example(("claims add emote_add @some_role", "claims add tag_add @some_other_role"))
    @ext.docs("Claims", "add")
    async def add(self, ctx: ext.ClemBotCtx, claim_t: ClaimsConverter, role: discord.Role) -> None:
        claim: Claims = t.cast(Claims, claim_t)

        if await self.bot.claim_route.check_claim_role(claim, role):
            embed = discord.Embed(
                title=f"Error: {claim.name} already added to {role.name}", color=Colors.Error
            )
            await ctx.send(embed=embed)
            return

        await self.bot.claim_route.add_claim_mapping(claim, role.id, raise_on_error=True)

        title = f'Claim: "{claim.name}" successfully added to role @{role.name} :white_check_mark:'

        claims = await self.bot.claim_route.get_claims_role(role.id)
        claims_str = "\n".join(c.name for c in claims)
        desc = f"Current {role.mention} claims ```\n{claims_str}```"

        embed = discord.Embed(title=title, color=Colors.ClemsonOrange, description=desc)
        await ctx.send(embed=embed)

    @claims.command(aliases=["delete"])
    @ext.required_claims(Claims.claims_modify)
    @ext.long_help("Removes a claim from a given role. ")
    @ext.short_help("Removes a claim from a given role")
    @ext.example(("claims remove emote_add @some_role", "claims delete tag_add @some_other_role"))
    @ext.docs("Claims", "remove")
    async def remove(
        self, ctx: ext.ClemBotCtx, claim_t: ClaimsConverter, role: discord.Role
    ) -> None:
        claim: Claims = t.cast(Claims, claim_t)

        if not await self.bot.claim_route.check_claim_role(claim, role):
            embed = discord.Embed(
                title=f"Error: {claim.name} not added to {role.name}", color=Colors.Error
            )
            await ctx.send(embed=embed)
            return

        title = (
            f'Claim: "{claim.name}" successfully removed from role @{role.name} :white_check_mark:'
        )

        await self.bot.claim_route.remove_claim_mapping(claim, role.id, raise_on_error=True)

        claims = await self.bot.claim_route.get_claims_role(role.id)
        claims_str = "\n".join(c.name for c in claims) if claims else "No current claims"
        desc = f"Current {role.mention} claims ```\n{claims_str}```"

        embed = discord.Embed(title=title, color=Colors.ClemsonOrange, description=desc)
        await ctx.send(embed=embed)

    @claims.command(aliases=["get"])
    @ext.long_help("Lists the currently available bot claims that can be assigned")
    @ext.short_help("Lists the available bot claims")
    @ext.example("claim list")
    @ext.docs("Claims", "list")
    async def list(self, ctx: ext.ClemBotCtx) -> None:
        claims_str = self.get_all_claims()

        embed = discord.Embed(
            title="Available Claims",
            color=Colors.ClemsonOrange,
            description=f"```\n{claims_str}```",
        )
        embed.set_footer(text=str(ctx.author), icon_url=ctx.author.display_avatar.url)

        await ctx.send(embed=embed)

    def get_all_claims(self) -> str:
        claims = [c for c, _ in Claims.__members__.items()]
        claims.sort()
        return "\n".join(claims) if claims else "No available claims"


async def setup(bot: ClemBot) -> None:
    await bot.add_cog(ClaimsAuthorizationCog(bot))
