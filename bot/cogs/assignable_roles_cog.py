import logging
import asyncio

import discord
import discord.ext.commands as commands
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
            await self.send_role_list(ctx, 'Assignable Roles')
            return
        
        try:
            role = await commands.RoleConverter().convert(ctx, input_role)

            if not await self.check_role_assignable(ctx, input_role):
                raise BadArgument

            await self.set_role(ctx, role)
        
        except BadArgument: # If RoleConverter failed
            await self.find_possible_roles(ctx, input_role)

    async def check_role_assignable(self, ctx, input_role: str) -> bool:
        assignable_roles = await RoleRepository().get_assignable_roles(ctx.guild.id) 
        return input_role in [ctx.guild.get_role(i['id']) for i in assignable_roles]

    async def find_possible_roles(self, ctx, input_role: str):
        # Casefold the roles
        str_input_role = str(input_role).casefold()

        assignable_roles = await RoleRepository().get_assignable_roles(ctx.guild.id) 
        role_list = [ctx.guild.get_role(i['id']) for i in assignable_roles]

        str_role_list = [str(i).casefold() for i in role_list] # Case-fold to do case insensitive matching

        # Compare input_role to role_list entries for matches
        matching_roles = []

        for j, val_j in enumerate(str_role_list):
            if str_input_role == val_j:
                matching_roles.append(role_list[j]) # matching_roles.append(j)
        
        role_count = len(matching_roles)

        if role_count == 0: # If no matches found, report findings
            await self.send_role_list(ctx, f'@{input_role} not found')
        elif role_count == 1: # If only one match was found, assign the role
            await self.set_role(ctx, matching_roles[0])
        else: # If multiple matches found, query user via emojis to select correct role
            await self.send_matching_roles_list(ctx, f'Multiple roles found for @{input_role}',
                matching_roles, role_count)

    async def send_matching_roles_list(self, ctx, title: str, matching_roles, role_count):
        names = ''
        reactions = ['\u0031\ufe0f\u20e3', '\u0032\ufe0f\u20e3', '\u0033\ufe0f\u20e3', '\u0034\ufe0f\u20e3',
                    '\u0035\ufe0f\u20e3', '\u0036\ufe0f\u20e3', '\u0037\ufe0f\u20e3', '\u0038\ufe0f\u20e3',
                    '\u0039\ufe0f\u20e3', '\U0001F51F']
        """
            USING EMOJIS WITH EMBEDDED TEXT
                What I know works:
                    1. Discord emoji name (e.g. ':pensive:')
                    2. Unicode emoji name (e.g. '\u0031\ufe0f\u20e3' or '\U0001F3D3')

                More info on using unicode emojis is provided below.
        """
        choose = '\n\n Please choose from one of the roles above.'

        for k, val_k in enumerate(matching_roles):
            if k < len(reactions):
                emojis = reactions[k] + ' '
            else:
                emojis = ''
            names = f'{names}\n{emojis}{val_k}'
        
        embed = discord.Embed(title= title, color= Colors.ClemsonOrange)
        embed.add_field(name= 'Matching Roles:', value= names + choose)

        mes = await ctx.send(embed= embed)
        
        # Remove unnecessary extra emojis from reactions list
        if role_count < len(reactions):
            del reactions[role_count:len(reactions)]

        """
            USING EMOJIS WITH d.py
                NOTE: This only works for UNICODE emojis. I have no idea how to get DISCORD specific emojis to work

                Guide: https://medium.com/@codingpilot25/how-to-print-emojis-using-python-2e4f93443f7e
                A list of emojis: https://www.unicode.org/emoji/charts/emoji-list.html
                
                Additional info: https://docs.python.org/3/reference/lexical_analysis.html#string-and-bytes-literals

                Method 1:
                say you want :ping_pong:, you would use the unicode charcter U+1F3D3 and change it to U0001F3D3.
                    thus, '\U0001F3D3' would be your string for ping pong
                as another example, if you wanted to use :skull_crossbones:, 
                you would use unicode character U+2620 and change it to U00002620
                    thus, '\U00002620' would be your string for skull and crossbones

                Method 2:
                Use the CDLR short names.
                Not recommended. Only works if name contains ONLY letters and spaces.
                #e.g. '{pensive face}' is fine but '{keycap: 1} would NOT work'
        """

        # Add reactions for user to choose from
        for str_emoji in reactions:
            await mes.add_reaction(str_emoji)

        # Validate the answer using a reaction event loop.
        def predicate(reaction: discord.Reaction, user: discord.Member) -> bool:
            # Test if the the answer is valid and can be evaluated.
            return (
                reaction.message.id == mes.id         # The reaction is attached to the question we asked.
                and user == ctx.author                # It's the user who triggered the initial role request.
                and str(reaction.emoji) in reactions  # The reaction is one of the options.
            )

        try:
            reaction, user = await ctx.bot.wait_for("reaction_add", timeout=10.0, check=predicate)
        except asyncio.TimeoutError:
            embed.add_field(name= 'Request Timeout:', value= 'User failed to respond in the alloted time', inline= 'false')
            await mes.edit(embed= embed)
            await mes.clear_reactions() # Remove reactions so use doesn't try to respond after timeout.
            return
        
        answer = reactions.index(reaction.emoji) # Get user reaction
        await self.set_role(ctx, matching_roles[answer]) # Attempt to assign user the requested role
        await mes.delete() # Delete message now that user has made a successful choice

    async def send_role_list(self, ctx, title: str):
        role_repo = RoleRepository()
        results = await role_repo.get_assignable_roles(ctx.guild.id)

        if results:
            names = '\n'.join([role['name'] for role in results])
        else:
            names = 'No currently assignable roles.'

        embed = discord.Embed(title= title, color= Colors.ClemsonOrange)
        embed.add_field(name= 'Available:', value= names)

        await ctx.send(embed= embed)

    async def set_role(self, ctx, role: discord.Role = None) -> None:
        role_repo = RoleRepository()

        if not await role_repo.check_is_role_assignable(role.id):
            await self.send_role_list(ctx, f'@{str(role)} is not an assignable role')
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

    @roles.command(pass_context= True, aliases= ['create'])
    @commands.has_guild_permissions(administrator = True)
    async def add(self, ctx, role: discord.Role = None) -> None:
        role_repo = RoleRepository()

        await role_repo.set_role_assignable(role.id, True)

        title = f'Role @{role.name} Added as assignable :white_check_mark:'
        embed = discord.Embed(title= title, color= Colors.ClemsonOrange)

        await ctx.send(embed= embed)

    @roles.command(pass_context= True, aliases= ['delete'])
    @commands.has_guild_permissions(administrator = True)
    async def remove(self, ctx, role: discord.Role = None) -> None:
        role_repo = RoleRepository()

        await role_repo.set_role_assignable(role.id, False)

        title = f'Role @{role.name} Removed as assignable :white_check_mark:'
        embed = discord.Embed(title= title, color= Colors.ClemsonOrange)

        await ctx.send(embed= embed)

    def get_full_name(self, author) -> str: 
        return f'{author.name}#{author.discriminator}' 

def setup(bot): 
    bot.add_cog(AssignableRolesCog(bot))