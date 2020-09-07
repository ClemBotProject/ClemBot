import logging
import os
from typing import List

import discord
import discord.ext.commands as commands
from bot.consts import Colors

log = logging.getLogger(__name__)


class SourceCodeCog(commands.Cog):
    """
    A cog to allow the bot to print its own source code given a file name
    """

    def __init__(self, bot) -> None:
        self.bot = bot
        self.bot_files = {}
        self.ignored = ['Logs/', 'venv/', '__pycache__/']

        for root, dirs, files in os.walk(os.getcwd(), topdown= True):
            dirs[:] = [d for d in dirs if not d.startswith('.')]
            if not any(folder in f'{root}/' for folder in self.ignored):
                for f in files:
                    self.bot_files[f] = os.path.join(root, f)

    @commands.command()
    async def source(self, ctx, file: str = None, line_start: int = None, line_stop: int = None):
        """
        Either prints the bots file structure as a tree or, if given a file, 
        prints out the source code of that file. the beginning and ending line numbers to be 
        printed can also be specified
        """

        if file is None:
            file_tree = self.list_files(os.getcwd(), self.ignored)
            for chunk in self.chunk_iterable(file_tree, 1980):
                await ctx.send(f'```yaml\n{chunk}```')
            return
        elif file == 'BotSecrets.json':
            embed = discord.Embed(title= f'Error: Restricted access', color= Colors.Error)
            await ctx.send(embed= embed)
            return
        else:
            file = file.replace('\\', '')
            file = file.replace('`', '')
        
        if line_start is not None and line_stop is not None:
            if line_start >= line_stop:
                embed = discord.Embed(title= f'Error: Line numbers are invalid', color= Colors.Error)
                await ctx.send(embed= embed)
                return

        try:
            open(self.bot_files[file])
        except (FileNotFoundError, KeyError):
            embed = discord.Embed(title= f'Error: File {file} not found', color= Colors.Error)
            await ctx.send(embed= embed)
            return

        with open(self.bot_files[file]) as f:
            source = f.read()

            if not source:
                return

            if line_stop is not None and len(source.splitlines()) <= line_stop:
                embed = discord.Embed(title= f'Error: End line number too high', color= Colors.Error)
                await ctx.send(embed= embed)
                return

            formatted_source = self.process_source(source, line_start, line_stop)
            total_chars = 0
            source_with_length = []
            #this creates a list of tuples (str, int) where the [1] index is the 
            #total character length of the source thus far
            for line in formatted_source:
                total_chars = total_chars + len(line)
                source_with_length.append((line, total_chars))

            #this walks the length list and breaks it into chunks based on 
            #the total char length thusfar
            break_point_increment = 1800
            break_point = break_point_increment
            chunks_to_send = []
            temp_list = []
            for _, value in enumerate(source_with_length):
                if value[1] < break_point:
                    #we havent reached the message char limit, keep going
                    temp_list.append(value[0])
                else:
                    #we hit the limit, stop and append to the chunk list
                    chunks_to_send.append('\n'.join(temp_list))

                    #clear the temp list and append the current line in the new 
                    #chunk so we dont lose it
                    temp_list.clear()
                    temp_list.append(value[0])

                    #increment the breakpoint so we know where the next chunk should end
                    break_point += break_point_increment

            #we enumerated over the whole list, append whats left to the chunks to send list
            chunks_to_send.append('\n'.join(temp_list))

            #loop over the chunks and send them one by one with correct python formatting
            for chunk in chunks_to_send:
                backslash = '\\'
                foo = len(chunk)
                await ctx.send(f"```py\n{chunk.replace('`', f'{backslash}`')}```")

    def chunk_iterable(self, iterable, chunk_size):
        for i in range(0, len(iterable), chunk_size):
            yield iterable[i:i + chunk_size]
    
    def process_source(self, source: str, line_start: int = None, line_stop: int = None):
        split_source = [f'{i}:    {value}' for i, value in enumerate(source.splitlines())]
        filtered_source = split_source[line_start or 0: line_stop or len(source)]

        return filtered_source
    
    def list_files(self, startpath, to_ignore: List[str]) -> str:
        tree = []
        for root, dirs, files in os.walk(startpath, topdown= True):
            dirs[:] = [d for d in dirs if not d.startswith('.')]
            if not any(folder in f'{root}/' for folder in to_ignore):
                level = root.replace(startpath, '').count(os.sep)
                indent = ' ' * 4 * (level)
                tree.append(f'{indent}{os.path.basename(root)}/')
                subindent = ' ' * 4 * (level + 1)
                for f in files:
                    tree.append(f'{subindent}{f}')
        return '\n'.join(tree)


def setup(bot):
    bot.add_cog(SourceCodeCog(bot))
