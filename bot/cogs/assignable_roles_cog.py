import logging
import asyncio

import discord
import discord.ext.commands as commands
from discord import Colour, Embed, File, Member, Message, Reaction
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
            await self.set_role(ctx, role)

        # If RoleConverter failed
        except BadArgument:
            # Casefold the roles
            str_input_role = str(input_role).casefold()
            role_list = ctx.guild.roles # Return list of roles
            str_role_list = [str(i).casefold() for i in role_list] # Case-fold to do case insensitive matching

            # Compare input_role to role_list entries for matches
            role_count, matching_roles = 0, []

            for j in range(len(str_role_list)):
                if str_input_role == str_role_list[j]:
                    #await self.set_role(ctx, role_list[j])
                    matching_roles.append(role_list[j]) # matching_roles.append(j)
                    role_count = role_count + 1
            
            if role_count == 0: # If no matches found, report findings
                await self.send_role_list(ctx, f'@{input_role} not found')
            elif role_count == 1: # If only one match was found, assign the role
                await self.set_role(ctx, matching_roles[0]) # role_list[k[0]])
            else: # If multiple matches found, query user via emojis to select correct role
                await self.send_matching_roles_list(ctx, f'Multiple roles found for @{input_role}', \
                    matching_roles, role_count)

                #for m in range(len(k)):
                #    await self.set_role(ctx, role_list[k[m]])

    async def send_matching_roles_list(self, ctx, title: str, matching_roles, role_count):
        #role_repo = RoleRepository()
        #results = await role_repo.get_assignable_roles(ctx.guild.id)
        names = ''
        reactions = ['\u0031\ufe0f\u20e3','\u0032\ufe0f\u20e3','\u0033\ufe0f\u20e3','\u0034\ufe0f\u20e3', \
                        '\u0035\ufe0f\u20e3','\u0036\ufe0f\u20e3','\u0037\ufe0f\u20e3','\u0038\ufe0f\u20e3', \
                        '\u0039\ufe0f\u20e3','\U0001F51F']
        """
            USING EMOJIS WITH EMBEDDED TEXT
                What I know works:
                    1. Discord emoji name (e.g. ':pensive:')
                    2. Unicode emoji name (e.g. '\u0031\ufe0f\u20e3' or '\U0001F3D3')
        """
        choose = '\n\n Please choose from one of the roles above.'

        for k in range(len(matching_roles)):
            if k < len(reactions):
                emojis = reactions[k] + ' '
            else:
                emojis = ''
            names = names + '\n' + emojis + str(matching_roles[k])
        
        embed = discord.Embed(title= title, color= Colors.ClemsonOrange)
        embed.add_field(name= 'Matching Roles:', value= names + choose)

        mes: Message = await ctx.send(embed= embed)
        
        # Remove unnecessary emojis
        if role_count < len(reactions):
            #print('\n' + str(len(reactions)) + '\n')
            del reactions[role_count:len(reactions)]

        """
            USING EMOJIS WITH d.py
                NOTE: This only works for UNICODE emojis. I have no idea how to get DISCORD specific emojis to work

                Guide: https://medium.com/@codingpilot25/how-to-print-emojis-using-python-2e4f93443f7e
                A list of emojis: https://www.unicode.org/emoji/charts/emoji-list.html
                
                Additional info: https://docs.python.org/3/reference/lexical_analysis.html#string-and-bytes-literals

                Method 1:
                say you wants :ping_pong:, you would use the unicode charcter U+1F3D3 and change it to U0001F3D3.
                    thus, '\U0001F3D3' would be your string for ping pong
                as another example, if you wanted to use :skull_crossbones:, you would use unicode character U+2620 and change it to U00002620
                    thus, '\U00002620' would be your string for skull and crossbones

                Method 2:
                Use the CDLR short names.
                Not recommended. Only worked if name contains ONLY letters and spaces.
        """
                #e.g. '\N{pensive face}' is fine but '\N{keycap: 1} would NOT work'

        # Add reactions for user to choose from
        for str_emoji in reactions:
            await mes.add_reaction(str_emoji)

        # Validate the answer using a reaction event loop.
        def predicate(reaction: Reaction, user: Member) -> bool:
            # Test if the the answer is valid and can be evaluated.
            return (
                reaction.message.id == mes.id         # The reaction is attached to the question we asked.
                and user == ctx.author                # It's the user who triggered the quiz.
                and str(reaction.emoji) in reactions  # The reaction is one of the options.
            )

        try:
            reaction, user = await ctx.bot.wait_for("reaction_add", timeout=90.0, check=predicate)
        except asyncio.TimeoutError: # was asyncio.
            await ctx.send(f'You took too long.')
            await mes.clear_reactions()
            return
        
        answer = -1
        
        for m in range(len(reactions)):
            if str(reaction.emoji) == reactions[m]:
                answer = m
        
        if answer > -1:
            await ctx.send(f'User reaction was associated with role **{reactions[answer]}**.')
            await self.set_role(ctx, matching_roles[answer])
        else:
            await ctx.send(
                f'User reaction was not associated with a role.'
            )

        await mes.clear_reactions()

        return

    async def send_role_list(self, ctx, title: str):
        role_repo = RoleRepository()
        results = await role_repo.get_assignable_roles(ctx.guild.id)

        if results:
            names = '\n'.join([role['name'] for role in results])
        else:
            names = 'No currently assignable roles'

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