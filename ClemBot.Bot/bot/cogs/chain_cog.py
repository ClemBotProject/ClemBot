import logging
import re
import typing as t
from copy import copy

import discord
import discord.ext.commands as commands

import bot.extensions as ext

log = logging.getLogger(__name__)


class ChainCog(commands.Cog):
    """This cog handles the chaining of commands"""

    def __init__(self, bot):
        self.bot = bot

    @ext.command()
    @ext.chainable(False)
    @ext.long_help('Chains multiple chainable commands together')
    @ext.short_help('Chains commands')
    @ext.example('chain command1 command2 hello')
    async def chain(self, ctx, *, text: str):
        prefix = await self.bot.get_prefix(ctx)
        if not any(sub in text for sub in prefix):
            await ctx.send(f'{prefix[2]}chain requires 1 or more commands to run')
            return
        # Make a Fake ctx to intercept ctx send
        fakectx = copy(ctx)  # We gotta use this as to not pass a reference to the ctx object
        resultqueue = []  # Intercepted sends will be stored here

        # Actually does the intercepting
        async def fakesend(embed):
            if type(embed) == discord.Embed:
                raise Exception('Chainable Command Output is not String')
            resultqueue.append(str(embed))

        fakectx.send = fakesend
        pattern = f'[\w\d\s.](?={prefix[0]}|{prefix[1]}|\\{prefix[2]})'  # Divide our input by the prefixes
        commandls = re.split(pattern, text)
        isfirstcommandatfirst = any(sub in commandls[0] for sub in prefix)
        for i in range(0, len(commandls)):
            secondpattern = f'^\\{prefix[2]}'
            commandls[i] = commandls[i].replace(prefix[0], '')
            commandls[i] = commandls[i].replace(prefix[1], '')
            commandls[i] = re.sub(secondpattern, '', commandls[i])
            commandls[i] = commandls[i].replace('\\' + prefix[2], prefix[2])  # Allows the use of escaped prefixes as
            # regular characters without invoking command
        # Main Loop
        index = len(commandls) - 1
        while index > (not isfirstcommandatfirst):
            buffer, err = await self.process_command(commandls.pop(index), True, fakectx)
            if buffer == 1:
                await ctx.send(err)
                return
            for i in range(0, len(resultqueue)):
                commandls[index - 1] += resultqueue[i]
                if i != len(resultqueue) - 1:
                    commandls[index - 1] += '\n'
            resultqueue = []
            index -= 1
        # Process the last command differently
        if isfirstcommandatfirst:  # If there is nothing before the last command then use the real ctx
            buffer, err = await self.process_command(commandls.pop(0), False, ctx)
            if buffer == 1:
                await ctx.send(err)
                return
        else:  # Otherwise pass the fake ctx so we can chain it
            buffer, err = await self.process_command(commandls.pop(1), True, fakectx)
            if buffer == 1:
                await ctx.send(err)
                return
            for i in range(0, len(resultqueue)):
                commandls[index - 1] += resultqueue[i]
                if i != len(resultqueue) - 1:
                    commandls[index - 1] += '\n'
            await ctx.send(commandls.pop(0))

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

    def boolcast(self, string):
        if string == 'False':
            return False
        if string == 'True':
            return True
        raise ValueError

    async def process_command(self, command, checkfordecorator, ctx):
        try:
            func = self.find_command(self.bot, command.split()[0])
        except IndexError:
            return 1, ' Empty command'
        if func is None:
            return 1, command.split()[0] + ' Is not a valid command'
        if checkfordecorator and not func.chainable_output:
            return 1, command.split()[0] + ' Is not a chainable command'
        if not checkfordecorator and not func.chainable_input and not func.chainable_output:
            return 1, command.split()[0] + ' Is not a chainable input command'

        args = {'context': ctx}
        temp = []
        for arg in func.params:
            if arg != 'self' and arg != 'ctx':
                temp.append(arg)
        if len(temp) == 1:
            index = command.find(' ')
            arg = ''
            if index != -1:
                arg = command[index:]
            args[temp[0]] = arg
        elif len(temp) == 0:
            return 1, command.split()[0] + ' Takes no arguments'
        else:
            remainder = command.split()
            remainder.pop(0)
            for i in range(0, len(temp) - 1):
                if type(func.params[temp[i]].annotation) == t._GenericAlias:
                    for arg in func.params[temp[i]].annotation.__args__:
                        try:
                            if arg == type(None):
                                pass
                            elif arg == bool:
                                args[temp[i]] = self.boolcast(remainder[0])
                                remainder.pop(0)
                                break
                            else:
                                args[temp[i]] = arg(remainder[0])
                                remainder.pop(0)
                                break
                        except ValueError:
                            pass  # This means that remainder[0] wasn't castable to that argument so we will move on to the next
                        except IndexError:
                            break  # Out of values
                elif func.params[temp[i]].annotation == bool:
                    try:
                        args[temp[i]] = self.boolcast(remainder[0])
                        remainder.pop(0)
                    except ValueError:
                        pass  # This means that remainder[0] wasn't castable to that argument so we will move on to the next
                    except IndexError:
                        break  # We ran out of arguments so continuing with command execution
                else:
                    try:
                        args[temp[i]] = func.params[temp[i]].annotation(remainder[0])
                        remainder.pop(0)
                    except ValueError:
                        pass  # This means that remainder[0] wasn't castable to that argument so we will move on to the next
                    except TypeError:
                        pass  # This means that remainder[0] wasn't castable to that argument so we will move on to the next
                    except IndexError:
                        break  # We ran out of arguments so continuing with command execution
            buffer = ''
            for i in range(0, len(remainder)):
                buffer += remainder[i]
                if i != len(remainder) - 1:
                    buffer += ' '
            args[temp[-1]] = buffer
        await func(**args)
        return 0, ''


def setup(bot):
    bot.add_cog(ChainCog(bot))
