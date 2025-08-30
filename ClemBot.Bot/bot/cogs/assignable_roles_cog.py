import asyncio

import discord
import discord.ext.commands as commands
from discord.ext.commands.errors import BadArgument

import bot.extensions as ext
from bot.clem_bot import ClemBot
from bot.consts import Claims, Colors
from bot.messaging.events import Events
from bot.utils.helpers import chunk_sequence
from bot.utils.logging_utils import get_logger

log = get_logger(__name__)

ROLE_LIST_CHUNK_SIZE = 15


class AssignableRolesCog(commands.Cog):
    """this is a test cog comment"""

    def __init__(self, bot: ClemBot) -> None:
        self.bot = bot

    @ext.group(invoke_without_command=True, aliases=["role"], case_insensitive=True)
    @ext.long_help("Lists all roles that have been marked as assignable in this server")
    @ext.short_help("Defines custom assignable roles")
    @ext.example("roles")
    @ext.docs(["Roles", "UserAssignableRoles"], "roles")
    async def roles(self, ctx: ext.ClemBotCtx, *, input_role: str | None = None) -> None:
        if input_role is None:
            await self.send_role_list(ctx, "Assignable Roles")
            return

        try:
            role = await commands.RoleConverter().convert(ctx, input_role)

            if not await self.bot.role_route.check_role_assignable(role.id):
                raise BadArgument

            await self.set_role(ctx, role)

        except BadArgument:  # If RoleConverter failed
            await self.find_possible_roles(ctx, input_role)

    async def check_role_assignable(self, ctx: ext.ClemBotCtx, input_role: str) -> bool:
        assert ctx.guild is not None
        assignable_roles = await self.bot.role_route.get_guilds_assignable_roles(ctx.guild.id)

        if not assignable_roles:
            return False

        roles = []
        for role in assignable_roles:
            r = ctx.guild.get_role(role.id)
            if r is not None:
                roles.append(r.name)
        return input_role in roles

    async def find_possible_roles(self, ctx: ext.ClemBotCtx, input_role: str) -> None:
        # Casefold the roles
        str_input_role = str(input_role).casefold()
        assert ctx.guild is not None
        assignable_roles = await self.bot.role_route.get_guilds_assignable_roles(ctx.guild.id)

        if not assignable_roles:
            return None

        str_role_list = [
            str(i.name).casefold() for i in assignable_roles
        ]  # Case-fold to do case-insensitive matching

        # Compare input_role to role_list entries for matches
        matching_roles = []

        for j, val_j in enumerate(str_role_list):
            if str_input_role == val_j:
                role = await commands.RoleConverter().convert(ctx, assignable_roles[j].name)
                matching_roles.append(role)  # matching_roles.append(j)

        role_count = len(matching_roles)

        if role_count == 0:  # If no matches found, report findings
            await self.send_role_list(ctx, f"@{input_role} not found")
        elif role_count == 1:  # If only one match was found, assign the role
            await self.set_role(ctx, matching_roles[0])
        else:  # If multiple matches found, query user via emojis to select correct role
            await self.send_matching_roles_list(
                ctx, f"Multiple roles found for @{input_role}", matching_roles, role_count
            )

    async def send_matching_roles_list(
        self, ctx: ext.ClemBotCtx, title: str, matching_roles: list[discord.Role], role_count: int
    ) -> None:
        names = ""
        reactions = [
            "\u0031\ufe0f\u20e3",
            "\u0032\ufe0f\u20e3",
            "\u0033\ufe0f\u20e3",
            "\u0034\ufe0f\u20e3",
            "\u0035\ufe0f\u20e3",
            "\u0036\ufe0f\u20e3",
            "\u0037\ufe0f\u20e3",
            "\u0038\ufe0f\u20e3",
            "\u0039\ufe0f\u20e3",
            "\U0001f51f",
        ]
        """
            USING EMOJIS WITH EMBEDDED TEXT
                What I know works:
                    1. Discord emoji name (e.g. ':pensive:')
                    2. Unicode emoji name (e.g. '\u0031\ufe0f\u20e3' or '\U0001f3d3')

                More info on using unicode emojis is provided below.
        """
        choose = "\n\n Please choose from one of the roles above."

        for k, val_k in enumerate(matching_roles):
            if k < len(reactions):
                emojis = reactions[k] + " "
            else:
                emojis = ""
            names = f"{names}\n{emojis}{val_k}"

        embed = discord.Embed(title=title, color=Colors.ClemsonOrange)
        embed.add_field(name="Matching Roles:", value=names + choose)

        mes = await ctx.send(embed=embed)

        # Remove unnecessary extra emojis from reactions list
        if role_count < len(reactions):
            del reactions[role_count : len(reactions)]

        """
            USING EMOJIS WITH d.py
                NOTE: This only works for UNICODE emojis. I have no idea how to get DISCORD specific emojis to work

                Guide: https://medium.com/@codingpilot25/how-to-print-emojis-using-python-2e4f93443f7e
                A list of emojis: https://www.unicode.org/emoji/charts/emoji-list.html

                Additional info: https://docs.python.org/3/reference/lexical_analysis.html#string-and-bytes-literals

                Method 1:
                say you want :ping_pong:, you would use the unicode charcter U+1F3D3 and change it to U0001F3D3.
                    thus, '\U0001f3d3' would be your string for ping pong
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
            # Test if the answer is valid and can be evaluated.
            return (
                reaction.message.id == mes.id  # The reaction is attached to the question we asked.
                and user == ctx.author  # It's the user who triggered the initial role request.
                and str(reaction.emoji) in reactions  # The reaction is one of the options.
            )

        try:
            reaction, _ = await ctx.bot.wait_for("reaction_add", timeout=10.0, check=predicate)
        except asyncio.TimeoutError:
            embed.add_field(
                name="Request Timeout:",
                value="User failed to respond in the allotted time",
                inline=False,
            )
            await mes.edit(embed=embed)
            await mes.clear_reactions()  # Remove reactions so use doesn't try to respond after timeout.
            return

        answer = reactions.index(reaction.emoji)  # Get user reaction
        await self.set_role(
            ctx, matching_roles[answer]
        )  # Attempt to assign user the requested role
        await mes.delete()  # Delete message now that user has made a successful choice

    async def send_role_list(self, ctx: ext.ClemBotCtx, title: str) -> None:
        assert ctx.guild is not None
        results = await self.bot.role_route.get_guilds_assignable_roles(ctx.guild.id)
        # list of all available roles
        pages = []

        if results:
            for chunk in chunk_sequence([role.name for role in results], ROLE_LIST_CHUNK_SIZE):
                embed = discord.Embed(title=title, color=Colors.ClemsonOrange)  # new
                embed.add_field(name="Available:", value="\n".join(chunk), inline=True)
                pages.append(embed)
        else:
            embed = discord.Embed(title=title, color=Colors.ClemsonOrange)
            embed.add_field(name="Available:", value="No currently assignable roles.")
            pages.append(embed)

        # Call paginate service
        await self.bot.messenger.publish(
            Events.on_set_pageable_embed,
            pages=pages,
            author=ctx.author,
            channel=ctx.channel,
            timeout=360,
        )

    async def set_role(self, ctx: ext.ClemBotCtx, role: discord.Role) -> None:

        if not await self.bot.role_route.check_role_assignable(role.id):
            await self.send_role_list(ctx, f"@{str(role)} is not an assignable role")
            return

        assert isinstance(ctx.author, discord.Member)

        if role.id in [r.id for r in ctx.author.roles]:
            await self.remove_role(ctx, role)
        else:
            await self.add_role(ctx, role)

    async def add_role(self, ctx: ext.ClemBotCtx, role: discord.Role) -> None:
        assert isinstance(ctx.author, discord.Member)
        await ctx.author.add_roles(role)

        embed = discord.Embed(title="Role Added  :white_check_mark:", color=Colors.ClemsonOrange)
        embed.add_field(name="Role: ", value=f"{role.mention} :arrow_right:")
        embed.add_field(name="User:", value=str(ctx.author))
        embed.set_thumbnail(url=ctx.author.display_avatar.url)

        await ctx.send(embed=embed)

    async def remove_role(self, ctx: ext.ClemBotCtx, role: discord.Role) -> None:
        assert isinstance(ctx.author, discord.Member)
        await ctx.author.remove_roles(role)

        embed = discord.Embed(title="Role Removed  :white_check_mark:", color=Colors.ClemsonOrange)
        embed.add_field(name="Role: ", value=f"{role.mention} :arrow_left:")
        embed.add_field(name="User:", value=str(ctx.author))
        embed.set_thumbnail(url=ctx.author.display_avatar.url)

        await ctx.send(embed=embed)

    @roles.command(pass_context=True, aliases=["create"])
    @ext.required_claims(Claims.assignable_roles_add)
    @ext.long_help("Command to add a role as assignable in the current guild")
    @ext.short_help("Marks a role as user assignable")
    @ext.example("roles add @SomeExampleRole")
    @ext.docs(["Roles", "UserAssignableRoles"], "add")
    async def add(self, ctx: ext.ClemBotCtx, *, role: discord.Role) -> None:
        await self.bot.role_route.set_assignable(role.id, True, raise_on_error=True)

        title = f"Role @{role.name} Added as assignable :white_check_mark:"
        embed = discord.Embed(title=title, color=Colors.ClemsonOrange)

        await ctx.send(embed=embed)

    @roles.command(pass_context=True, aliases=["delete"])
    @ext.required_claims(Claims.assignable_roles_delete)
    @ext.long_help("Command to remove a role as assignable in the current guild")
    @ext.short_help("Removes a role as user assignable")
    @ext.example("roles delete @SomeExampleRole")
    @ext.docs(["Roles", "UserAssignableRoles"], "remove")
    async def remove(self, ctx: ext.ClemBotCtx, *, role: discord.Role) -> None:
        await self.bot.role_route.set_assignable(role.id, False, raise_on_error=True)

        title = f"Role @{role.name} Removed as assignable :white_check_mark:"
        embed = discord.Embed(title=title, color=Colors.ClemsonOrange)

        await ctx.send(embed=embed)

    @roles.group(invoke_without_command=True, case_insensitive=True)
    @ext.long_help("Command to list all currently auto assigned roles in the guild")
    @ext.short_help("Removes a role as auto assigned")
    @ext.example("roles auto")
    @ext.docs(["Roles", "AutoAssignableRoles"], "roles-auto")
    async def auto(self, ctx: ext.ClemBotCtx) -> None:
        roles = await self.bot.role_route.get_guilds_auto_assigned_roles(ctx.guild.id)

        if not roles:
            embed = discord.Embed(
                title="No roles are currently auto assigned on join", color=Colors.ClemsonOrange
            )
            embed.add_field(name="Available:", value="No currently auto assigned roles.")
            await ctx.send(embed=embed)
            return

        pages = []
        if roles:
            mentions: list[str] = []
            for role in roles:
                d_role = ctx.guild.get_role(role.id)

                if not d_role:
                    mentions.append(role.name)
                    continue

                mentions.append(d_role.mention)

            for chunk in chunk_sequence(mentions, ROLE_LIST_CHUNK_SIZE):
                embed = discord.Embed(
                    title="Roles auto assigned on join", color=Colors.ClemsonOrange
                )  # new
                embed.add_field(name="Auto roles:", value="\n".join(chunk), inline=True)
                pages.append(embed)

        # Call paginate service
        await self.bot.messenger.publish(
            Events.on_set_pageable_embed,
            pages=pages,
            author=ctx.author,
            channel=ctx.channel,
            timeout=360,
        )

    @auto.command(name="add", aliases=["create"])
    @ext.required_claims(Claims.assignable_roles_add)
    @ext.long_help("Command to add a role as auto assigned in the current guild")
    @ext.short_help("Marks a role as auto assigned")
    @ext.example("roles auto add @SomeExampleRole")
    @ext.docs(["Roles", "AutoAssignableRoles"], "auto-add")
    async def auto_add(self, ctx: ext.ClemBotCtx, *, role: discord.Role) -> None:

        roles = await self.bot.role_route.get_guilds_auto_assigned_roles(ctx.guild.id)

        if role.id in [r.id for r in roles]:
            embed = discord.Embed(
                title=f"Error: @{role.name} already set as auto assigned", color=Colors.Error
            )
            await ctx.send(embed=embed)
            return

        await self.bot.role_route.set_auto_assigned(role.id, True)

        title = f"Role @{role.name} Added as an auto assigned on join role :white_check_mark:"
        embed = discord.Embed(title=title, color=Colors.ClemsonOrange)

        await ctx.send(embed=embed)

    @auto.command(name="remove", aliases=["delete"])
    @ext.required_claims(Claims.assignable_roles_delete)
    @ext.long_help("Command to remove a role as auto assigned in the current guild")
    @ext.short_help("Removes a role as auto assigned")
    @ext.example("roles auto remove @SomeExampleRole")
    @ext.docs(["Roles", "AutoAssignableRoles"], "auto-remove")
    async def auto_remove(self, ctx: ext.ClemBotCtx, *, role: discord.Role) -> None:

        roles = await self.bot.role_route.get_guilds_auto_assigned_roles(ctx.guild.id)

        if role.id not in [r.id for r in roles]:
            embed = discord.Embed(
                title=f"Error: @{role.name} not set as auto assigned", color=Colors.Error
            )
            await ctx.send(embed=embed)
            return

        await self.bot.role_route.set_auto_assigned(role.id, False)

        title = f"Role @{role.name} Removed as an auto assigned on join role :white_check_mark:"
        embed = discord.Embed(title=title, color=Colors.ClemsonOrange)

        await ctx.send(embed=embed)


async def setup(bot: ClemBot) -> None:
    await bot.add_cog(AssignableRolesCog(bot))
