import asyncio
import concurrent.futures
import logging
import os
import subprocess
import uuid

import discord
import discord.ext.commands as commands
import pylatex
from pdf2image import convert_from_path

import bot.extensions as ext
from bot.consts import Colors
from bot.messaging.events import Events

log = logging.getLogger(__name__)

COMPILER = 'pdflatex'
DOCUMENT_CLASS = 'standalone'
GEOMETRY_OPTIONS = {'margin': '0in'}
DOCUMENT_OPTIONS = 'preview, fleqn, border=5pt, varwidth=false'
# Temporary file save location - change if needed!
ASSETS_FOLDER = 'bot/cogs/latex_cog/assets/'
FILE_EXTENSIONS = ['.png', '.tex', '.pdf', '.aux', '.log']


def gen_tex_images(file_name: str, doc: pylatex.Document):
    pdf = file_name + '.pdf'
    doc.generate_pdf(file_name, clean_tex=True, compiler=COMPILER, silent=True)
    images = convert_from_path(pdf, fmt='png', transparent=True, single_file=True)
    os.remove(pdf)
    for image in images:
        image = image.crop(image.getbbox())
        image.save(file_name + '.png', 'PNG')
    return images


def _cleanup_files(file_name: str):
    for extension in FILE_EXTENSIONS:
        try:
            os.remove(file_name + extension)
        except OSError:
            log.error(f'Failed to delete ${file_name + extension}')


class LatexCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @ext.command()
    @ext.short_help('TeX-ify me!')
    @ext.long_help('A command to generate TeX images.')
    @ext.example(['latex $1+2$', 'latex $\\sqrt{2}$', 'latex $\\frac{1}{2}$'])
    async def latex(self, ctx, *, tex: str):
        msg = await self._generating_embed(ctx)
        loop = asyncio.get_event_loop()
        doc = pylatex.Document(documentclass=DOCUMENT_CLASS,
                               document_options=DOCUMENT_OPTIONS,
                               geometry_options=GEOMETRY_OPTIONS,
                               lmodern=True,
                               font_size='LARGE')
        doc.preamble.append(pylatex.utils.NoEscape('\\everymath{\\displaystyle}\n'))
        doc.packages.append(pylatex.Package('xcolor'))
        tex = pylatex.utils.NoEscape('\\color{white}\n' + tex + '\n')
        doc.append(tex)
        temp_name = ASSETS_FOLDER + str(uuid.uuid4())
        with concurrent.futures.ProcessPoolExecutor() as pool:
            args = (temp_name, doc)
            try:
                await loop.run_in_executor(pool, gen_tex_images, *args)
            except subprocess.CalledProcessError:
                await msg.delete()
                await self._syntax_embed_log(ctx, temp_name)
                return
        await msg.delete()
        attachment = discord.File(fp=f'{temp_name}.png')
        msg = await ctx.send(file=attachment)
        await self.bot.messenger.publish(Events.on_set_deletable, msg=msg, author=ctx.author, timeout=60)
        _cleanup_files(temp_name)

    async def _generating_embed(self, ctx) -> discord.Message:
        """Shorthand for sending an embed saying the image is being generated"""
        embed = discord.Embed(title=':hourglass_flowing_sand: Generating Image', color=Colors.ClemsonOrange,
                              description='Generating image, please wait...\n\n'
                                          '_This may take longer than a few seconds._')
        embed.set_footer(text=f'{ctx.author.name}#{ctx.author.discriminator}', icon_url=ctx.author.display_avatar.url)
        return await ctx.send(embed=embed)

    async def _syntax_embed_log(self, ctx, temp_name: str):
        """Shorthand for sending an embed with the log to show cause of error"""
        embed = discord.Embed(title='Error', color=Colors.Error, description='No valid image generated.\n'
                                                                             'Please check your syntax and try again.')
        embed.set_footer(text=f'{ctx.author.name}#{ctx.author.discriminator}', icon_url=ctx.author.display_avatar.url)
        attachment = discord.File(fp=f'{temp_name}.log')
        msg = await ctx.send(embed=embed, file=attachment)
        await self.bot.messenger.publish(Events.on_set_deletable, msg=msg, author=ctx.author, timeout=60)
        _cleanup_files(temp_name)

    async def _error_embed(self, ctx, desc: str):
        """Shorthand for sending an error embed w/ consistent formatting"""
        embed = discord.Embed(title='Error', color=Colors.Error, description=desc)
        embed.set_footer(text=f'{ctx.author.name}#{ctx.author.discriminator}', icon_url=ctx.author.display_avatar.url)
        msg = await ctx.send(embed=embed)
        await self.bot.messenger.publish(Events.on_set_deletable, msg=msg, author=ctx.author, timeout=60)


def setup(bot):
    bot.add_cog(LatexCog(bot))
