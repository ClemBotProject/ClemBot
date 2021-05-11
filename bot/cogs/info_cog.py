import logging
import discord 
import discord.ext.commands as commands
import bot.extensions as ext
from bot.consts import Colors
from bot.data.message_repository import MessageRepository
from bot.consts import Claims
from bot.data.moderation_repository import ModerationRepository
from bot.clem_bot import ClemBot

log = logging.getLogger(__name__)

class InfoCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
    
    @ext.command()
    @ext.long_help('Provides information about either a given user or the calling user, depending on its invocation, relating to their account and guild related information. Can take in a user\'s mention, ID, or nothing if the calling user wants information about themselves.')
    @ext.short_help('Provides user and guild information about a guild member.')
    @ext.example(('info @user', 'info 123456789', 'info'))
    @ext.required_claims(Claims.moderation_infraction_view)
    @ext.ignore_claims_pre_invoke()
    async def info(self, ctx, member: discord.Member = None):
        #If the command is invoked without a specified member, it will return info on the calling user
        if not member:
            member = ctx.author
        log.info(f'User {ctx.author} has ran info command on user {member.name}')

        embed = discord.Embed(title = f'Guild Member Information', color=Colors.ClemsonOrange)
        user_info = f'» **Nickname:** {member.mention}'
        user_info += f'\n» **ID:** {member.id}'
        user_info += f'\n» **Username:** {member.name}#{member.discriminator}'
        #Some info doesn't need to be available to anyone to check
        if await self.bot.claims_check(ctx=ctx):
            user_info += f'\n» **Created:** {member.created_at}'
        embed.add_field(name='**Member ID:**', value=user_info)
        embed.set_thumbnail(url=member.avatar_url)

        guild_info = ''
        if await self.bot.claims_check(ctx=ctx) is True:
            guild_info = f'» **Joined:** {member.joined_at}'
        guild_info += f'\n» **Message count (last 30 days):** {await MessageRepository().get_user_message_count_range(member.id, member.guild.id, 30)}'
        guild_info += f'\n» **Roles:** '
        log.info(f'User has roles: {member.roles}')
        #skipping the first index because it is just @everyone
        for i in member.roles[1::]:
            guild_info += f'{i.mention}'
        guild_info += f'\n» **Highest role:** {member.top_role.mention}'
        guild_info += f'\n» **Nitro boost date:** {member.premium_since}'
        embed.add_field(name='**Guild Information:**', value=guild_info)
        
        if await self.bot.claims_check(ctx=ctx) is True:
            moderation_info = f'» **Warnings:** {len(await ModerationRepository().get_all_warns_member(member.guild.id, member.id))}'
            moderation_info += f'\n» **Active Mutes:** {len(await ModerationRepository().get_all_active_mutes_member(member.guild.id, member.id))}'
            moderation_info += f'\n» **Total Infractions:** {len(await ModerationRepository().get_all_infractions_member(member.guild.id, member.id))}'
            embed.add_field(name='**Moderation Info:**', value=moderation_info)
        await ctx.send(embed=embed)
        

def setup(bot):
    bot.add_cog(InfoCog(bot))
    