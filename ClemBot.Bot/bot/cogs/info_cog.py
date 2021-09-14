from bot.api.message_route import MessageRoute
import logging
import discord
import discord.ext.commands as commands
import bot.extensions as ext
from bot.consts import Colors, Claims
from bot.messaging.events import Events
DEFAULT_MESSAGE_RANGE = 30
log = logging.getLogger(__name__)

class InfoCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @ext.command()
    @ext.required_claims(Claims.moderation_infraction_view)
    @ext.ignore_claims_pre_invoke()
    async def info(self, ctx, user: discord.User = None):
        #Default range for message count 30 days(~1 month)
        

        #If the command is invoked without a specified user, it will return info on the calling user
        if not user:
            user = ctx.author
        
        log.info(f'User {ctx.author} has ran info command on user {user.name}')

        embed = discord.Embed(title = f'Guild Member Information', color=Colors.ClemsonOrange)
        embed.set_author(name=str(user), icon_url=user.display_avatar.url)

        user_info = f'» **Nickname:** {user.mention}'
        user_info += f'\n» **ID:** {user.id}'
        #Some info doesn't need to be available to anyone to check on for other users
        claims = await self.bot.claim_route.get_claims_user(ctx.author)
        if (await self.bot.claims_check(ctx=ctx)) or (ctx.author.id == user.id): 
            #prints the datetime in the format of <Months> <day> <year> <hours>:<minutes>:<seconds> <AM/PM>
            user_info += '\n» **Created:** ' + user.created_at.strftime('%b %d %Y %I:%M:%S %p')

        embed.add_field(name='**User ID:**', value=user_info)
        embed.set_thumbnail(url=user.display_avatar.url)

        #since member objects include guild ID's and information, we try to get a member object for the target user
        member = ctx.guild.get_member(user.id)
        #check to see if the target user is in the calling context's guild. If None then the user isn't in the calling server
        if member:

            # We don't want moderation info available for regular guild users to check on others
            if await self.bot.claims_check(ctx=ctx): 
                warnings = await self.bot.moderation_route.get_guild_warns_user(ctx.guild.id, user.id)
                mutes = await self.bot.moderation_route.get_guild_mutes_user(ctx.guild.id, user.id)
                infractions = await self.bot.moderation_route.get_guild_infractions_user(ctx.guild.id, user.id)

                moderation_info = f'» **Warnings:** {0 if warnings is None else len(warnings)} '
                moderation_info += f'\n» **Mutes:** {0 if mutes is None else len(mutes)}'
                moderation_info += f'\n» **Total Infractions:** {0 if infractions is None else len(infractions)}'
                embed.add_field(name='**Moderation Info:**', value=moderation_info)

            guild_info = ''
            if (ctx.command.claims_check(claims)) or (ctx.author.id == user.id):
                #prints the datetime in the format of <Months> <day> <year> <hours>:<minutes>:<seconds> <AM/PM>
                guild_info = '» **Joined:** ' + member.joined_at.strftime('%b %d %Y %I:%M:%S %p') 

            guild_info += f'\n» **Message count (last 30 days):** {await self.bot.message_route.range_count_messages(user.id, ctx.guild.id, DEFAULT_MESSAGE_RANGE)}'
            guild_info += f'\n» **Roles:** '
            log.info(f'User has roles: {member.roles}')
            #skipping the first index because it is just @everyone
            for i in member.roles[1:]:
                guild_info += f'{i.mention}\t'

            guild_info += f'\n» **Highest role:** {member.top_role.mention}'
            guild_info += '\n» **Nitro boost date:** ' + (member.premium_since.strftime('%b %d %Y %I:%M:%S %p') if member.premium_since is not None else 'Not boosting')
            embed.add_field(name='**Guild Information:**', value=guild_info, inline=False)

        embed.set_footer(text=f'{ctx.author.name}#{ctx.author.discriminator}', icon_url=ctx.author.display_avatar.url)
        msg = await ctx.send(embed=embed)
        await self.bot.messenger.publish(Events.on_set_deletable, msg=msg, author=ctx.author)

def setup(bot):
    # This adds the cog internally by creating a cog instance and registering that
    bot.add_cog(InfoCog(bot))
