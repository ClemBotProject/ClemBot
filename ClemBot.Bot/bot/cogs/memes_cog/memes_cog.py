import concurrent.futures
import datetime
import io
import logging
import os
import random
import time
import typing as t

import discord
import discord.ext.commands as commands
from PIL import Image, ImageDraw, ImageSequence, ImageFont

import bot.extensions as ext
from bot.consts import Colors
from bot.messaging.events import Events

log = logging.getLogger(__name__)
MAX_WALDO_GRID_SIZE = 100
CRAB_LINE_LENGTH = 58
CRAB_COMMAND_COOLDOWN = 3


def pillow_process(args, lines_in_text, timestamp):
    # Open crab.gif and add our font
    with Image.open('bot/cogs/memes_cog/assets/crab.gif') as im:
        fnt = ImageFont.truetype('bot/cogs/memes_cog/assets/LemonMilk.otf', 11)

        # Draw text on each frame of the gif
        # Gonna be honest I don't quite understand how it works but I got it from the Pillow docs/issues
        frames = []
        for frame in ImageSequence.Iterator(im):
            frame = frame.quantize(colors=254) # quantize to make color palette size 254, leaving room for white and ClemsonOrange
            d = ImageDraw.Draw(frame)
            w, h = d.textsize(args, fnt)
            # draws the text on to the frame. Tries to center horizontally and tries to go as close to the bottom as possible
            d.text((im.size[0] / 2 - w / 2, im.size[1] - h - (7 * lines_in_text)), args, font=fnt, align='center',
                   fill="#ffffff", stroke_width=2, stroke_fill=f'#{hex(Colors.ClemsonOrange)[2:]}', spacing=6)
            del d

            b = io.BytesIO()
            frame.save(b, format='GIF')
            frame = Image.open(b)
            frames.append(frame)
        frames[0].save(f'bot/cogs/memes_cog/assets/out_{timestamp}.gif', save_all=True, append_images=frames[1:])


class MemesCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @ext.command()
    @ext.long_help(
        'A fun command to generate a pseudo bubblewrap effect in discord'
    )
    @ext.short_help('Creates bubblewrap!')
    @ext.example('bubblewrap')
    async def bubblewrap(self, ctx):

        msg = ''
        for _ in range(0, 5):
            for _ in range(0, 10):
                msg += '||pop!|| '
            msg += '\n'

        await ctx.send(msg)

    @commands.command()
    @ext.long_help(
        'A fun command to generate a wheres waldo effect in discord, see if you can find him first!'
        'Optionally takes a size parameter to make it easier or harder'
    )
    @ext.short_help('Can you find him?')
    @ext.example(('waldo', 'waldo 10'))
    async def waldo(self, ctx, size=MAX_WALDO_GRID_SIZE):

        """
        Play Where's Waldo!

        Usage: <prefix>waldo [size = 100]
        """
        random_start_letters = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'X',
                                'Y', 'Z']

        max_waldo_line_size = 6
        new_line_waldo_chance = 10
        msg = ''
        count = 0
        place = random.randint(0, size)

        for i in range(size + 1):
            if i == place:
                msg += '||`WALDO`|| '
                count += 1
            else:
                helper = random.randint(0, len(random_start_letters) - 1)
                letter = random_start_letters[helper]
                msg += f'||`{letter}ALDO`|| '
                count += 1

            new_line = random.randint(0, 100)

            if new_line < new_line_waldo_chance or count > max_waldo_line_size:
                msg += '\n'
                count = 0

        await ctx.send(msg)

    @ext.command()
    @ext.chainable()
    @ext.long_help(
        'A fun command to spongebob meme text in discord'
    )
    @ext.short_help('sO yOu doNt KnOw wHat tHiS Is?')
    @ext.example('spongebob hello world')
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

        await ctx.send(result)

    @ext.command(aliases=['rave', '🦀'])
    @commands.cooldown(1, CRAB_COMMAND_COOLDOWN, commands.BucketType.guild)
    @ext.long_help(
        'A fun command to generate a crab rave gif with specified text overlay'
    )
    @ext.short_help('Generates a crab rave gif')
    @ext.chainable_input()
    @ext.example('crab hello from crab world')
    async def crab(self, ctx, *, args='Bottom text\n is dead'):
        """
        Create your own crab rave.
        Usage: <prefix>crab [text=Bottom text\\n is dead]
        Aliases: rave, 🦀
        """
        # crab.gif dimensions - 352 by 200
        # Immediately grab the timestamp incase of multiple calls in a row
        timestamp = datetime.datetime.utcnow().microsecond
        wait_msg = await ctx.send('Generating your gif')
        args = args.replace('\\', '')

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
            pil_args = (args, lines_in_text, timestamp)
            await loop.run_in_executor(pool, pillow_process, *pil_args)

        # Attach, send, and delete created gif
        attachment = discord.File(filename=f'out_{timestamp}.gif', fp=f'bot/cogs/memes_cog/assets/out_{timestamp}.gif')
        msg = await ctx.send(file=attachment)
        await self.bot.messenger.publish(Events.on_set_deletable, msg=msg, author=ctx.author)
        await wait_msg.delete()
        os.remove(f'bot/cogs/memes_cog/assets/out_{timestamp}.gif')

    @ext.command(hidden=True, aliases=['ctray', 'trayforjay'])
    async def cookouttray(self, ctx, input):
        """
        For those who do finances with cookout trays, we proudly present the command for you
            Simply type one of the following:
                cookouttray
                ctray
                trayforjay

            Followed by a monetary value such as (leave off the dollar sign):
                20
                100
                3.14

            To have it converted into cookout trays
                Examples:
                    cookouttray 20
                    ctray 100
                    trayforjay 3.14

        Clicking the link "Cash to Cookout Tray Converter" in the output will also take you to cookout's website
        """
        money = round(float(input), 2)
        output = money / 5

        embed = discord.Embed(
            title='Cash to Cookout Tray Converter',
            description=f'{ctx.message.author.mention} ${money} is approximately {output} cookout trays',
            url=f"https://www.fastfoodmenuprices.com/cookout-prices/",
            color=Colors.ClemsonOrange)
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(MemesCog(bot))
