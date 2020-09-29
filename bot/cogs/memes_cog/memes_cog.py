import logging
import random
import time
import io
import os
import datetime
import concurrent.futures
import typing as t

import discord
import discord.ext.commands as commands
from PIL import Image, ImageDraw, ImageSequence, ImageFont

from bot.consts import Colors

log = logging.getLogger(__name__)
MAX_WALDO_GRID_SIZE = 100
CRAB_LINE_LENGTH = 58
CRAB_COMMAND_COOLDOWN = 3

def pillow_process(args, is_rave, lines_in_text, timestamp):
    # Open crab.gif and add our font
    im = Image.open('bot/cogs/memes_cog/assets/crab.gif')
    fnt = ImageFont.truetype('bot/cogs/memes_cog/assets/LemonMilk.otf', 11)
    
    # Draw text on each frame of the gif
    # Gonna be honest I don't quite understand how it works but I got it from the Pillow docs/issues
    frames = []
    for frame in ImageSequence.Iterator(im):
        d = ImageDraw.Draw(frame)
        w, h = d.textsize(args, fnt)
        # draws the text on to the frame. Tries to center horizontally and tries to go as close to the bottom as possible
        d.text((im.size[0]/2 - w/2, im.size[1] - h - (5 * lines_in_text)), args, font=fnt, align='center',
            stroke_width=bool(is_rave), stroke_fill=Colors.ClemsonOrange, spacing=6)
        del d

        b = io.BytesIO()
        frame.save(b, format='GIF')
        frame = Image.open(b)
        frames.append(frame)
    frames[0].save(f'bot/cogs/memes_cog/assets/out_{timestamp}.gif', save_all=True, append_images=frames[1:])

class MemesCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
    
    @commands.command()
    async def bubblewrap(self, ctx):

        msg = ''
        for _ in range(0, 5):
            for _ in range(0, 10):
                msg += '||pop!|| '
            msg += '\n'

        await ctx.send(msg)

    @commands.command()
    async def waldo(self, ctx, size=MAX_WALDO_GRID_SIZE):

        """
        Play Where's Waldo!

        Usage: <prefix>waldo [size = 100]
        """
        random_start_letters = ['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','X','Y','Z']

        max_waldo_line_size = 6
        new_line_waldo_chance = 10
        msg = ''
        count = 0
        place = random.randint(0,size)

        for i in range(size+1):
            if i == place:
                msg += '||`WALDO`|| '
                count += 1
            else:
                helper = random.randint(0,len(random_start_letters)-1)
                letter = random_start_letters[helper]
                msg += f'||`{letter}ALDO`|| '
                count += 1
            
            new_line = random.randint(0,100)

            if new_line < new_line_waldo_chance or count > max_waldo_line_size:
                msg += '\n'
                count = 0

        await ctx.send(msg)

    @commands.command()
    async def spongebob(self, ctx, *, args):

        """
        Spongebob Text
        """
        random.seed(time.time())
        args = args.replace('"', "'")
    
        result = ''
        for i in args:
            helper = random.randint(0, 100)
            
            if helper > 60:
                result += str(i).upper()
            else:
                result += str(i).lower()

        embed = discord.Embed(title="SpOnGeBoB", color=Colors.ClemsonOrange)
        result2 = ''

        # Discord messages can only be 2k characters long, this block accounts for that
        if len(result) >= 1024:
            result2 = result[1024:len(result)]
            result = result[:1023]
        embed.add_field(name="TeXt", value=result, inline=False)

        if result2:
            embed.add_field(name="tExT", value=result2, inline=False)
        

        await ctx.send(embed=embed)

    @commands.command(aliases=['rave', '🦀'])
    @commands.cooldown(1, CRAB_COMMAND_COOLDOWN, commands.BucketType.guild)
    async def crab(self, ctx, is_rave: t.Optional[bool] = True, *, args='Bottom text\n is dead'):
        """
        Create your own crab rave.
        Usage: <prefix>crab [is_rave=True] [text=Bottom text\\n is dead]
        Aliases: rave, 🦀
        """
        # crab.gif dimensions - 352 by 200
        # Immediately grab the timestamp incase of multiple calls in a row
        timestamp = datetime.datetime.utcnow()
        msg = await ctx.send('Generating your gif')
        
        # Add new lines for when the text would go out of bounds
        lines_in_text = 1
        while len(args) > (CRAB_LINE_LENGTH * lines_in_text):
            newline_loc = CRAB_LINE_LENGTH * lines_in_text
            # I didn't want to add a newline in the middle of a word
            while not args[newline_loc].isspace():
                newline_loc -= 1
                if newline_loc == CRAB_LINE_LENGTH * (lines_in_text - 1):
                    newline_loc = CRAB_LINE_LENGTH * lines_in_text
                    break

            args = f'{args[:newline_loc]} \n{args[newline_loc:]}'
            lines_in_text += 1
        
        loop = self.bot.loop
        with concurrent.futures.ProcessPoolExecutor() as pool:
            pil_args = (args, is_rave, lines_in_text, timestamp)
            await loop.run_in_executor(pool, pillow_process, *pil_args)

        # Attach, send, and delete created gif
        attachment = discord.File(filename=f'out_{timestamp}.gif', fp=f'bot/cogs/memes_cog/assets/out_{timestamp}.gif')
        await ctx.send(file=attachment)
        await msg.delete()
        os.remove(f'bot/cogs/memes_cog/assets/out_{timestamp}.gif')

    @commands.command(aliases=['8ball',"🎱"])
    async def ball(self, ctx, *, question):
        """
        A simple magic 8 ball than can be used with 'ball' or '8ball'
		Example:
			ball Will I have a good day today?
			8ball Will I have a bad day today?
			"""
        responses = [
			"It is certain.",
			"It is decidedly so.",
			"Without a doubt.",
			"Yes – definitely.",
			"You may rely on it.",
			"As I see it, yes.",
			"Most likely.",
			"Outlook good.",
			"Yes.",
			"Signs point to yes.",
			"Reply hazy, try again.",
			"Ask again later.",
			"Better not tell you now.",
			"Cannot predict now.",
			"Concentrate and ask again.",
			"Don't count on it.",
			"My reply is no.",
			"My sources say no.",
			"Outlook not so good.",
			"Very doubtful."
			]
        embed = discord.Embed(title="🎱", description= f"{random.choice(responses)}",color = Colors.ClemsonOrange)
        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(MemesCog(bot))
