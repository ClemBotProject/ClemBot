import logging
import math
import typing as t

import discord
import discord.ext.commands as commands
import requests
from PIL import Image, UnidentifiedImageError

import bot.extensions as ext
from bot.consts import Colors

log = logging.getLogger(__name__)
ASCIIYDOTS = 4
ASCIIXDOTS = 2
PC_WIDTH = 59
MOBILE_WIDTH = 23
# having this at the actual threshold of 2000 caused issues around
# Just best to give some leniency
CHAR_LIMIT = 1950


class DotCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    # So, I made this from a copy of image-to-braille. I am modifying the
    # file to work for discord mobile, and desktop

    # main source code I am replicating. Find here:
    # https://lachlanarthur.github.io/Braille-ASCII-Art/dist/index.js
    # and here: https://github.com/zepthro/image-to-braille

    # https://stackoverflow.com/questions/14681609/create-a-2d-list-out-of-1d-list
    # usuage (list of 1d elements, n elements per line )
    # 2x2 matrix is the_data = [1,2,3,4] n = 2
    def to_matrix(self, the_data, n):
        return [the_data[i:i + n] for i in range(0, len(the_data), n)]

    # requires grayscale images
    # https://stackoverflow.com/questions/31572425/list-all-rgba-values-of-an-image-with-pil

    def image_data_to_braille(self, rgb_array, inverted, threshold):
        # The original author used subarrays in this function.
        # I am taking a slightly different method than the original author, because the rgb_array is grayscale. 
        # Hence, why I do not need to get another subarray
        # A GREAT READ: https://en.wikipedia.org/wiki/Braille_Patterns
        # I did not know anything about braille until this project
        # The following line sets up the 4x2 array the wiki article mentions
        dots = [rgb_array[0][0], rgb_array[1][0], rgb_array[2][0], rgb_array[0][1], rgb_array[1][1], rgb_array[2][1], rgb_array[3][0],
                rgb_array[3][1]]
        # make the image a binary value for each gray scale value
        # if you want an inverted image, you flip dots >= threshold to dots < threshold
        # or simply not(...)
        # or the bitwise not operator on the result
        for i in range(len(dots)):
            dots[i] = chr(ord('1') - inverted) if dots[i] >= threshold else chr(ord('0') + inverted)
        # now we do some more vodoo magic
        # actually quite clever technique of binary representation of braille
        # again, see https://en.wikipedia.org/wiki/Braille_Patterns
        # braille starts at hex(0x2800) or int(10240)
        dots.reverse()
        return str(chr(0x2800 + int(''.join(dots), 2)))

    def parse_image(self, image, asciiWidth, threshold, inverted):
        # necessary to have a gray scaled image. Can do this with a conversion
        # or simply finding the average of (r,g,b) per pixel value
        rgb_pixels = image.convert('L')
        width, height = rgb_pixels.size

        # new image height. Want to proportionately make the image fit the screen
        # not sure the exact conversion calculation here.
        asciiHeight = math.ceil(asciiWidth * ASCIIXDOTS * (height / width) / ASCIIYDOTS)
        # want equal number of asciiDots. i.e. 4x2 array
        width = asciiWidth * ASCIIXDOTS
        height = asciiHeight * ASCIIYDOTS
        rgb_pixels = rgb_pixels.resize((width, height)).getdata()
        # conversion of a 1d array to 2d array
        two_d_array = self.to_matrix(list(rgb_pixels), width)

        # fix the dimensions to not exceed Discord's character limit
        while (width * height) / (ASCIIXDOTS * ASCIIYDOTS) > CHAR_LIMIT:
            width -= ASCIIXDOTS
            height -= ASCIIYDOTS

        # now time for the magic
        finished_image = []

        # want to make small subsets of the image. i.e. section the image in asciiHeight*asciiWidth
        # sections.
        # . .
        # . .
        # . .
        # . .
        for y in range(0, height, ASCIIYDOTS):
            line_of_braille = ''
            for x in range(0, width, ASCIIXDOTS):
                # want to get that subsection now. starting in corner (x,y) to (width,height).
                # in our case we want ASCIIXDOTS width, and ASCIIYDOTS height
                # referencing: https://stackoverflow.com/questions/38049214/how-to-obtain-a-subarray-in-python-3
                # we want to get a subset of the image. We can easily use a package like numpy, but
                # relying on numpy makes the project dependencies huge.
                line_of_braille += self.image_data_to_braille([sub[x:x + ASCIIXDOTS] for sub in two_d_array[y:y + ASCIIYDOTS]], inverted, threshold)

            finished_image.append(line_of_braille)
        return finished_image

    async def todots_helper(self, ctx, image, device=None, threshold=150, inverted=False) -> None:
        filename = image

        if device is None or device.lower() == 'pc':
            width = PC_WIDTH
        elif device.lower() == 'mobile':
            width = MOBILE_WIDTH
        else:
            # return an error here
            embed = discord.Embed(title=f'ERROR: Invalid image width', color=Colors.Error)
            embed.add_field(name='Exception:', value="Width must either be 'mobile' or 'pc'.\n Default length is 'pc' length.")
            await ctx.send(embed=embed)
            return

        if threshold not in range(0, 256):
            # errors
            embed = discord.Embed(title=f'ERROR: threshold must be 0 <= threshold <= 255', color=Colors.Error)
            embed.add_field(name='Exception:', value='threshold not a valid int or in range.')
            await ctx.send(embed=embed)
            return
        # intentionally not converting to a 2d array here. If someone, or myself, wants to
        # add a 1d array functionality, great! I am sticking with 2d arrays right now. 
        # check if we need to open a file, or a url
        # https://github.com/FranciscoMoretti/asciify-color/blob/master/asciify.py
        # https://stackoverflow.com/questions/7391945/how-do-i-read-image-data-from-a-url-in-python
        new_img = []
        try:
            # meant when the person wants to exclude the embed in a regular message
            # breaks the bot otherwise
            filename = filename.replace('<', '').replace('>', '')
            with Image.open(requests.get(filename, stream=True).raw) as img:
                # default asciiWidth I found online. Aparently over 500 gets laggy
                new_img = self.parse_image(img, width, threshold, inverted)
                await ctx.send('\n'.join(new_img))
        except UnidentifiedImageError as e:
            embed = discord.Embed(title=f'ERROR: unable to open message link', color=Colors.Error)
            embed.add_field(name='Exception:', value=filename + ' link does not exist, or is broken!')
            await ctx.send(embed=embed)

    @ext.group(invoke_without_command=True)
    @ext.long_help('Takes any image, and returns the brailled image. '
                   'Can specify mobile or pc width characteristics. '
                   'Default width is pc size. '
                   'Choose a width of \'pc\', \'mobile\', or leave blank. '
                   'Threshold determines which pixels are white, and which are blank. Choose a value [0-255] '
                   'The final argument asks, do you want to invert the image or not? '
                   'When attachment specifier is used, you can upload an image directly. All other arguments '
                   'are the same except you no longer need a url for the first argument')
    @ext.short_help('Turn an image to a braille image. '
                    'Default width is pc size. '
                    'Default threshold is 150. '
                    'To specify threshold you must include all required arguments. '
                    'The same goes for all arguments')
    @ext.example(('todots https://my-cool-image.com/stuff.jpg [mobile|pc] [threshold = 0-255] [inverted = 0/1]',
                  'todots https://my-cool-image.com/stuff.jpg [mobile|pc] [threshold = 0-255]',
                  'todots https://my-cool-image.com/stuff.jpg [mobile|pc]',
                  'todots https://my-cool-image.com/stuff.jpg'))
    async def todots(self, ctx, image, device=None, threshold=150, inverted: t.Optional[bool] = False) -> None:
        return await self.todots_helper(ctx, image, device, threshold, inverted)

    @todots.command()
    @ext.long_help('Takes any image, and returns the brailled image. '
                   'Can specify mobile or pc width characteristics. '
                   'Default width is pc size. '
                   'Choose a width of \'pc\', \'mobile\', or leave blank. '
                   'Threshold determines which pixels are white, and which are blank. Choose a value [0-255] '
                   'The final argument asks, do you want to invert the image or not? '
                   'When attachment specifier is used, you can upload an image directly. Must attach an image.')
    @ext.short_help('Turn an attached image to a braille image. '
                    'Default width is pc size. '
                    'Default threshold is 150. '
                    'To specify threshold you must include all required arguments. '
                    'The same goes for all arguments. Must attach an image')
    @ext.example(('todots attachment [mobile|pc] [threshold = 0-255] [inverted = 0/1]',
                  'todots attachment [mobile|pc] [threshold = 0-255]',
                  'todots attachment [mobile|pc]',
                  'todots attachment'))
    async def attachment(self, ctx, device=None, threshold=150, inverted: t.Optional[bool] = False) -> None:
        try:
            image = ctx.message.attachments[0].url
        except Exception as e:
            embed = discord.Embed(title=f'ERROR: must include an attached image', color=Colors.Error)
            embed.add_field(name='Exception:', value="upload an image when using 'attachment' specifier")
            await ctx.send(embed=embed)
            return
        return await self.todots_helper(ctx, image, device, threshold, inverted)


def setup(bot):
    bot.add_cog(DotCog(bot))
