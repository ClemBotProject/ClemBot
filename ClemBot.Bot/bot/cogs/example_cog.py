# import the logging framework to allow us to log internally
# what the bot does
import logging

# import the discord specific libraries we will use
import discord
import discord.ext.commands as commands

# import the internal command extension libraries to mark methods as commands
import bot.extensions as ext

# get a module level logger using the __name__ of the module as the root,
# this will link it with the base logger bot. and all out put will be through that
log = logging.getLogger(__name__)


# We create a class with the postfix of "Cog"
# and make sure it inherits from Commands.cog
class ExampleCog(commands.Cog):
    """None"""
    """
    This is an example cog to demonstrate the expected layout of a cog with commands
    A cog is a grouping of bot commands that serve similar functions 
    for more info see the documentation
    https://discordpy.readthedocs.io/en/latest/ext/commands/cogs.html
    """

    # entry point of the cog, the d.py library supplies us with the bot
    # parameter which is the client object of the running bot
    # its with this that we can access all parts of the discord api
    def __init__(self, bot):
        self.bot = bot
        self._last_member = None

    # To createa a command you decorate an async method with ext.command
    # the command name in discord will be the name of the function that you have decorated
    # so to invoke this command, if your prefix was !, youd type !hello in discord
    @ext.command()
    # Decorator to define the long form version of the help command, this will be shown when some does !help <your_command_name>
    @ext.long_help('Says hello to whoever invoked this command')
    # Decorator to define the short form version of the help command, this will be shown on the default help page listing
    @ext.short_help('Tells you hello')
    # Decorator to define the example of the help command, this is to give users an actual usage example for your command
    # do not include the prefix in your example the help command will add the prefix in accordance with the context its called from
    @ext.example('hello')
    async def hello(self, ctx, *, member: discord.Member = None):
        # self is a python OOP concept, if you are unfamilar brush up on how python handles classes
        # ctx is the context from which the command was invoked from, it contains the message, the guild
        # the command was sent in, the channel, etc
        # it provodes contextual metadata about how the command was invoked
        member = member or ctx.author
        if self._last_member is None or self._last_member.id != member.id:
            msg = await ctx.send(f'Hello {member.name}!')
        else:
            await ctx.send(f'Hello {member.name}... This feels familiar :thinking:')
        self._last_member = member

    # temporary placement till i can do it better
    @ext.command(hidden=True)
    @commands.has_guild_permissions(administrator=True)
    async def slowmode(self, ctx, value: int):
        await ctx.channel.edit(slowmode_delay=value)
        await ctx.send(f'Slowmode set to {value}')


# This is the setup function at the module level, d.py expects this function to
# load cogs into the library internally
def setup(bot):
    # This adds the cog internally by creating a cog instance and registering that
    bot.add_cog(ExampleCog(bot))
