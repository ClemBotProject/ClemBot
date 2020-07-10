import logging

import discord
from discord.colour import Color
import discord.ext.commands as commands
from discord.ext.commands.converter import RoleConverter
from discord.ext.commands.errors import BadArgument

from bot.data.role_repository import RoleRepository
from bot.consts import Colors

log = logging.getLogger(__name__)


class AssignableRolesCog(commands.Cog):

    def __init__(self, bot) -> None:
        self.bot = bot
    
    @commands.group(pass_context= True, invoke_without_command= True, aliases= ['role'])
    async def roles(self, ctx, *, input_role: str = None) -> None:

        if input_role is None:
            await self.send_channel_list(ctx, 'Assignable Roles')
            return
        
        try:
            role = await commands.RoleConverter().convert(ctx, input_role)
        except BadArgument:
            await self.send_channel_list(ctx, f'@{input_role} not found')
            return
        
        await self.set_role(ctx, role)

    async def send_channel_list(self, ctx, title: str):
        role_repo = RoleRepository()
        results = await role_repo.get_assignable_roles(ctx.guild.id)

        if results:
            names = '\n'.join([role['name'] for role in results])
        else:
            names = 'No currently assignable channels'

        embed = discord.Embed(title= title, color= Colors.ClemsonOrange)
        embed.add_field(name= 'Available:', value= names)

        await ctx.send(embed= embed)

    async def set_role(self, ctx, role: discord.Role = None) -> None:
        role_repo = RoleRepository()

        if not await role_repo.check_is_role_assignable(role.id):
            embed = discord.Embed(title= f'@{role.name} is not assignable', color= Colors.Error)
            await ctx.send(embed= embed)
            return

        if role.id in [role.id for role in ctx.author.roles]:
            await self.remove_role(ctx, role)
        else:
            await self.add_role(ctx, role)

    async def add_role(self, ctx, role: discord.Role):
        await ctx.author.add_roles(role)

        embed = discord.Embed(title= f'Role Added  :white_check_mark:', color= Colors.ClemsonOrange)
        embed.add_field(name= f'Role: ', value= f'{role.mention} :arrow_right:')
        embed.add_field(name= 'User:', value= f'{self.get_full_name(ctx.author)}')
        embed.set_thumbnail(url= ctx.author.avatar_url_as(static_format= 'png'))

        await ctx.send(embed= embed)

    async def remove_role(self, ctx, role: discord.Role):
        await ctx.author.remove_roles(role)

        embed = discord.Embed(title= f'Role Removed  :white_check_mark:', color= Colors.ClemsonOrange)
        embed.add_field(name= f'Role: ', value= f'{role.mention} :arrow_left:')
        embed.add_field(name= 'User:', value= f'{self.get_full_name(ctx.author)}')
        embed.set_thumbnail(url= ctx.author.avatar_url_as(static_format= 'png'))

        await ctx.send(embed= embed)

    @roles.command(pass_context= True)
    @commands.has_role('Admin')
    async def add(self, ctx, role: discord.Role = None, aliases= ['create']) -> None:
        role_repo = RoleRepository()

        await role_repo.set_role_assignable(role.id, True)

        title = f'Role #{role.name} Added as assignable :white_check_mark:'
        embed = discord.Embed(title= title, color= Colors.ClemsonOrange)

        await ctx.send(embed= embed)

    @roles.command(pass_context= True)
    @commands.has_role('Admin')
    async def remove(self, ctx, role: discord.Role = None, aliases= ['delete']) -> None:
        role_repo = RoleRepository()

        await role_repo.set_role_assignable(role.id, False)

        title = f'Role #{role.name} Removed as assignable :white_check_mark:'
        embed = discord.Embed(title= title, color= Colors.ClemsonOrange)

        await ctx.send(embed= embed)

    def get_full_name(self, author) -> str: 
        return f'{author.name}#{author.discriminator}' 

def setup(bot): 
    bot.add_cog(AssignableRolesCog(bot))