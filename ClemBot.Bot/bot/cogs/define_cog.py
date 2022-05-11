# This contribution was made by: Rajat Sethi
# Date: 12/15/2020

import logging
import re
import unicodedata

import aiohttp
import discord
import discord.ext.commands as commands

import bot.bot_secrets as bot_secrets
import bot.extensions as ext
from bot.consts import Colors
from bot.messaging.events import Events

log = logging.getLogger(__name__)
API_URL = 'https://www.dictionaryapi.com/api/v3/references/collegiate/json/'


class defineCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    def getPageData(self, jsonData, word):
        pages = []

        # If the word is not found and there are no suggestions.
        if not jsonData:
            return ['Word not found.']

        # If the word is found, the JSON will return a dictionary of information.
        if isinstance(jsonData[0], dict):

            # For words with several definitions, it will return several dictionaries.
            for wordData in jsonData:
                # Stems of the given word (Past Tense, Future Tense, Perfect Tense, etc.)
                wordStems = wordData.get('meta', {}).get('stems', [])

                # Syllables of the given word
                syllableData = wordData.get('hwi', {}).get('hw', '')

                # Pronunciation of the given word (With those weird letters)
                pronunc = []
                prsData = wordData.get('hwi', {}).get('prs', [])

                for soundData in prsData:
                    pronunc.append(soundData.get('mw', ''))

                # Type of the given word (Noun, Verb, Adjective, etc.)
                wordType = wordData.get('fl', '')

                # Definitions of the given word
                definitions = []
                defData = wordData.get('shortdef', [])

                for defin in defData:
                    definitions.append(defin)

                # Turn data into one long string (represents a page)
                template = 'Tenses: '
                for s in enumerate(wordStems):
                    template += s[1]
                    if s[0] != len(wordStems) - 1:
                        template += ', '
                template += '\n'

                template += f'Syllables: {syllableData}\n'

                template += 'Pronunciation: '
                for s in enumerate(pronunc):
                    template += s[1]
                    if s[0] != len(pronunc) - 1:
                        template += ', '
                template += '\n'

                template += f'Word Type: {wordType}\n'

                template += '\n'
                for s in enumerate(definitions):
                    page = f'{template}Definition: {s[1]}'
                    page = page.replace('*', ' | ')
                    pages.append(page)

        # If the word cannot be found, the JSON returns a list of other possible suggestions.
        elif isinstance(jsonData[0], str):
            template = f'Word not found, see also: '
            for s in enumerate(jsonData):
                template = f'{template} {s[1]}'
                if s[0] != len(jsonData) - 1:
                    template = f'{template}, '

            pages = [template]

        return pages

    @ext.command()
    @ext.long_help(
        'Gets the dictionary defintion of any given word'
    )
    @ext.short_help('Gets a words definition')
    @ext.example('define hello')
    async def define(self, ctx, word):
        """
        Given a word, find its definition and any other relevant information

        USE: define <word>
        EXAMPLE: define schadenfreude

        For phrases, use underscores
        EXAMPLE: define computer_science

        Letters, numbers, and special characters (_, &, and -) are supported
        """

        self.api_key = bot_secrets.secrets.merriam_key

        # Break down the unicode string to split up any special characters into their base parts
        # Ex: U+0239 (ï) -> U+0105 (i) + U+0776 (diaeresis modifier)
        word = unicodedata.normalize('NFKD', word)
        # Remove any characters besides &, _, or - that are not in ranges a-z, A-Z, or 0-9
        # per the ASCII Table https://www.asciitable.com
        word = re.sub("[^a-zA-Z0-9 &_-]+", "", word)

        actualWord = word.replace('_', ' ')
        word = word.replace('_', '%20').lower()

        if len(word) == 0:
            embed = discord.Embed(title='Merriam-Webster Dictionary', color=Colors.Error)
            ErrMsg = 'Unable to parse word out of argument'
            embed.add_field(name='Error', value=ErrMsg, inline=False)
            await ctx.send(embed=embed)
            return

        url = f'{API_URL}{word}?key={self.api_key}'
        wordPages = []

        # Try Except for catching errors that could give away the API key
        try:
            async with aiohttp.request('get', url) as response:
                if response.status == 200:
                    jsonData = await response.json()
                    wordPages = self.getPageData(jsonData, word)

                else:
                    embed = discord.Embed(title='Merriam-Webster Dictionary', color=Colors.Error)
                    ErrMsg = f'Oh No! There appears to be an issue! Yell at one of the developers with the following code.\nError Code: {response.status}'
                    embed.add_field(name='Error with API', value=ErrMsg, inline=False)
                    await ctx.send(embed=embed)
                    return

                await self.bot.messenger.publish(Events.on_set_pageable_text,
                                                 embed_name='Merriam-Webster Dictionary',
                                                 field_title=f'Word: {actualWord}',
                                                 pages=wordPages,
                                                 author=ctx.author,
                                                 channel=ctx.channel)
        except Exception as err:
            err_str = str(err)
            err_str = re.sub(self.api_key, "CLASSIFIED", err_str)
            raise Exception(err_str).with_traceback(err.__traceback__)


def setup(bot):
    bot.add_cog(defineCog(bot))
