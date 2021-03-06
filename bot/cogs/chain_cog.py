import logging

import discord
import discord.ext.commands as commands
from copy import copy

import bot.extensions as ext

log = logging.getLogger(__name__)

class ChainCog(commands.Cog):
    """This cog handles the chaining of commands"""

    def __init__(self, bot):
        self.bot = bot
        self.resultqueue = []

    @ext.command()
    @ext.chainable_output(False)
    @ext.long_help('Chains multiple chainable commands together')
    @ext.short_help('Chains commands')
    @ext.example('chain command1 command2 hello')
    async def chain(self, ctx, *, text: str):
        prefix = str(await self.bot.current_prefix(ctx))
        # Make a fake ctx to intercept values passed to send
        fakectx = copy(ctx)
        fakectx.send = self.fakesend
        # The first command doesnt have to have a chainable output so processed later
        try:
            command1 = text[text.index(prefix)+1:text.index(' ')]
        except ValueError:
            await ctx.send("no valid first command")
            return
        remainder = text[text.index(' ')+1:]
        # Get output of the chainable output commands
        while(True):
            currentcommandindex = remainder.rfind(prefix)
            if currentcommandindex == -1:
                # If no more commands, break
                break
            currentcommand = self.find_command(self.bot, remainder[currentcommandindex+1:remainder.index(' ',currentcommandindex)])
            if currentcommand is None:
                # if the command isnt valid, stop execution
                await ctx.send(remainder[currentcommandindex + 1:remainder.index(' ', currentcommandindex)]+' is not a valid command')
                return
            if currentcommand.chainable_output:
                argname = str(next(reversed(currentcommand.params.values())))
                buffer = argname.find('=')
                if buffer != -1:
                    argname = argname[:buffer]
                # Run the command passing the fake ctx
                await eval('currentcommand(' + argname + '= \''+remainder[remainder.index(' ', currentcommandindex)+1:]+'\', ctx=fakectx)')
                # Create new remainder, getting rid of the command and replacing it with the result of the executed command
                remainder = remainder[:currentcommandindex]
                for buffer in self.resultqueue:
                    if type(buffer)== discord.Embed:
                        for field in buffer.fields:
                            remainder += str(field.value)
                    else:
                        remainder += str(buffer)
                self.resultqueue.clear()
            else:
                # if the command doesnt have a chainable output, stop execution
                await ctx.send(currentcommand.qualified_name+' is not chainable')
                return
        # After all the chainable output commands have been ran, run the last command
        command1func = self.find_command(self.bot, command1)
        if command1func is None:
            await ctx.send(command1+" is not a valid command")
            return
        argname = str(next(reversed(command1func.params.values())))
        buffer = argname.find('=')
        if buffer!=-1:
            argname = argname[:buffer]
        # Pass the real ctx as this is the last command to be executed
        await eval('command1func('+argname+'=remainder, ctx=ctx)')

    async def fakesend(self, embed):
        self.resultqueue.append(embed)


    # Code Copied from help_cog.py
    def find_command(self, parent, command_name: str):
        """
        Recursively searches the command tree to find a given command, if none found then returns None
        """
        if isinstance(parent, commands.Bot):
            found = None
            for c in parent.commands:
                if result := self.find_command(c, command_name):
                    found = result
            return found

        if parent.qualified_name == command_name:
            return parent

        if isinstance(parent, ext.ClemBotGroup):
            for c in parent.commands:
                if result := self.find_command(c, command_name):
                    return result
        return None

def setup(bot):
    bot.add_cog(ChainCog(bot))
