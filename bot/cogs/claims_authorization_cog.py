import typing as t

import discord
import discord.ext.commands as commands

import bot.extensions as ext
from bot.data.claims_repository import ClaimsRepository
from bot.utils.converters import ClaimsConverter
from bot.consts import Colors, Claims

class ClaimsAuthorizationCog(commands.Cog):

    def __init__(self, bot) -> None:
        self.bot = bot
    
    @ext.group(invoke_without_command=True, aliases=['auth', 'claim'])
    @ext.required_claims(Claims.claims_view)
    @ext.long_help(
        'Claims represent privileges within the bot. ' 
        'Each claim gives access to different functionality and can be added to as many '
        'roles as desired'
    )
    @ext.short_help('Claims authorization setup')
    @ext.example(('claims', 'claims @some_role', 'claims @some_user'))
    async def claims(self, ctx: commands.Context, listing: t.Union[discord.Role, discord.Member]=None):
        user = None
        role = None

        if isinstance(listing, discord.Role):
            role = listing
        elif isinstance(listing, discord.Member):
            user = listing

        if role:
            await self._send_role_claims(ctx, role)
        else:
            await self._send_user_claims(ctx, user or ctx.author)
    
    async def _send_role_claims(self, ctx, role):
        repo = ClaimsRepository()
        claims = await repo.fetch_all_claims_role(role)

        embed = self._build_claims_embed(ctx, claims) 
        await ctx.send(embed=embed)
        
    async def _send_user_claims(self, ctx, user):
        repo = ClaimsRepository()
        claims = await repo.fetch_all_claims_user(user)

        embed = self._build_claims_embed(ctx, claims) 
        await ctx.send(embed=embed)
    
    def _build_claims_embed(self, ctx, claims) -> discord.Embed:

        claims = list(claims)
        claims.sort()
        claims_str = '\n'.join(claims) if claims else 'No current claims'

        embed = discord.Embed(title='Current Valid Claims', color=Colors.ClemsonOrange, description=f'```\n{claims_str}```')
        embed.set_footer(text=self.get_full_name(ctx.author), icon_url=ctx.author.avatar_url)
        return embed


    @claims.command(aliases=['set'])
    @ext.required_claims(Claims.claims_modify)
    @ext.long_help(
        'Adds a claim to a given role. ' 
        'Who ever has that role will have access to that functionality'
    )
    @ext.short_help('Add claims to a given role')
    @ext.example(('claims add emote_add @some_role', 'claims add tag_add @some_other_role'))
    async def add(self, ctx, claim: ClaimsConverter, role: discord.Role):
        repo = ClaimsRepository()
        if await repo.check_claim_role(claim, role):
            embed = discord.Embed(title=f'Error: {claim.name} already added to {role.name}', color=Colors.Error)
            await ctx.send(embed=embed)
            return

        await repo.add_claim_mapping(claim.name, role)

        title = f'Claim: "{claim.name}" successfully added to role @{role.name} :white_check_mark:'

        claims = await repo.fetch_all_claims_role(role)
        claims_str = "\n".join(claims)
        desc = f'Current {role.mention} claims ```\n{claims_str}```' 

        embed = discord.Embed(title=title, color=Colors.ClemsonOrange, description=desc)
        await ctx.send(embed=embed)

    @claims.command(aliases=['delete'])
    @ext.required_claims(Claims.claims_modify)
    @ext.long_help(
        'Removes a claim from a given role. ' 
    )
    @ext.short_help('Removes a claim from a given role')
    @ext.example(('claims remove emote_add @some_role', 'claims delete tag_add @some_other_role'))
    async def remove(self, ctx, claim: ClaimsConverter, role: discord.Role):
        repo = ClaimsRepository()
        if not await repo.check_claim_role(claim, role):
            embed = discord.Embed(title=f'Error: {claim.name} not added to {role.name}', color=Colors.Error)
            await ctx.send(embed=embed)
            return

        title = f'Claim: "{claim.name}" successfully removed from role @{role.name} :white_check_mark:'

        claims = await repo.fetch_all_claims_role(role)
        claims_str = '\n'.join(claims) if claims else 'No current claims'
        desc = f'Current {role.mention} claims ```\n{claims_str}```' 

        embed = discord.Embed(title=title, color=Colors.ClemsonOrange, description=desc)
        await ctx.send(embed=embed)
        await repo.remove_claim_mapping(claim.name, role)

    @claims.command(aliases=['get'])
    @ext.long_help(
        'Lists the currently available bot claims that can be assigned' 
    )
    @ext.short_help('Lists the available bot claims')
    @ext.example('claim list')
    async def list(self, ctx):
        claims = [c for c, _ in Claims.__members__.items()]
        claims.sort()
        claims_str = '\n'.join(claims) if claims else 'No available claims'

        embed = discord.Embed(title='Available Claims', color=Colors.ClemsonOrange, description=f'```{claims_str}```')
        embed.set_footer(text=self.get_full_name(ctx.author), icon_url=ctx.author.avatar_url)
 
        await ctx.send(embed=embed)

    def get_full_name(self, author) -> str: 
        return f'{author.name}#{author.discriminator}' 

def setup(bot): 
    bot.add_cog(ClaimsAuthorizationCog(bot))