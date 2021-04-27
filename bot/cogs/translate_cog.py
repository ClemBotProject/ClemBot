import json
import logging
import uuid

import aiohttp
import discord
import discord.ext.commands as commands
from discord.ext.commands.errors import UserInputError

import bot.extensions as ext
from bot.bot_secrets import BotSecrets
from bot.consts import Colors
from bot.messaging.events import Events

log = logging.getLogger(__name__)

LANGUAGE_NAME_TO_SHORT_CODE = {
    "afrikaans": "af",
    "arabic": "ar",
    "bulgarian": "bg",
    "catalan": "ca",
    "chinese simplified": "zh-hans",
    "chinese traditional": "zh-hant",
    "croatian": "hr",
    "czech": "cs",
    "danish": "da",
    "dutch": "nl",
    "english": "en",
    "estonian": "et",
    "finnish": "fi",
    "french": "fr",
    "german": "de",
    "greek": "el",
    "gujarati": "gu",
    "haitian creole": "ht",
    "hebrew": "he",
    "hindi": "hi",
    "hungarian": "hu",
    "icelandic": "is",
    "indonesian": "id",
    "irish": "ga",
    "italian": "it",
    "japanese": "ja",
    "klingon": "tlh-latn",
    "korean": "ko",
    "kurdish (central)": "ku-arab",
    "latvian": "lv",
    "lithuanian": "lt",
    "malay": "ms",
    "maltese": "mt",
    "norwegian": "nb",
    "pashto": "ps",
    "persian": "fa",
    "polish": "pl",
    "portuguese": "pt",
    "romanian": "ro",
    "russian": "ru",
    "serbian (cyrillic)": "sr-cyrl",
    "serbian (latin)": "sr-catn",
    "slovak": "sk",
    "slovenian": "sl",
    "spanish": "es",
    "swahili": "sw",
    "swedish": "sv",
    "tahitian": "ty",
    "thai": "th",
    "turkish": "tr",
    "ukrainian": "uk",
    "urdu": "ur",
    "vietnamese": "vi",
    "welsh": "cy",
    "yucatec maya": "yua"
}
CHUNK_SIZE = 15
LANGUAGE_SHORT_CODE_TO_NAME = {value: key for key, value in LANGUAGE_NAME_TO_SHORT_CODE.items()}

TRANSLATE_API_URL = "https://api.cognitive.microsofttranslator.com/translate"

TRACE_ID = str(uuid.uuid4())


class TranslateCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @ext.group(case_insensitive=True, invoke_without_command=True)
    @ext.long_help(
        'Allows you to translate words or sentences by either specifying both the input and output language with the text to translate, or just the output language and the text to translate. run \'translate languages\' to see available languages')
    @ext.short_help('Translates words or phrases between two languages')
    @ext.example(('translate en spanish Hello', 'translate german Hello', 'translate languages', 'translate Spanish German Como estas?'))
    async def translate(self, ctx, *input: str):
        if len(input) < 2:
            raise UserInputError("Incorrect Number of Arguments. Minimum of 2 arguments")

        if is_valid_lang_code(input[1]):
            await self.translate_given_lang(ctx, input)
        else:
            await self.translate_detect_lang(ctx, input)

    @translate.command()
    @ext.long_help('Shows all available languages to translate between')
    @ext.short_help('Shows available languages')
    @ext.example(('translate languages'))
    async def languages(self, ctx):
        await self.bot.messenger.publish(Events.on_set_pageable_text,
                                         embed_name='Languages',
                                         field_title='Here are the available languages:',
                                         pages=get_language_list(self),
                                         author=ctx.author,
                                         channel=ctx.channel)
        return

    async def translate_given_lang(self, ctx, input):
        input_lang = await get_lang_code(self, ctx, input[0])
        output_lang = await get_lang_code(self, ctx, input[1])

        if input_lang == None or output_lang == None:
            return

        text = ' '.join(input[2:])

        log.info(f'Input Lang Code: {input_lang}')
        log.info(f'Output Lang Code: {output_lang}')
        params = {
            'api-version': '3.0',
            'from': input_lang,
            'to': output_lang
        }

        body = [{
            'text': text
        }]

        headers = {
            'Ocp-Apim-Subscription-Key': BotSecrets.get_instance().azure_translate_key,
            'Ocp-Apim-Subscription-Region': 'global',
            'Content-type': 'application/json',
            'X-ClientTraceId': TRACE_ID
        }

        async with aiohttp.ClientSession() as session:
            async with await session.post(url=TRANSLATE_API_URL, params=params, headers=headers, json=body) as resp:
                response = json.loads(await resp.text())

        log.info(response[0]['translations'])
        embed = discord.Embed(title='Translate', color=Colors.ClemsonOrange)
        name = 'Translated to ' + LANGUAGE_SHORT_CODE_TO_NAME[response[0]['translations'][0]['to'].lower()]
        embed.add_field(name=name, value=response[0]['translations'][0]['text'], inline=False)
        await ctx.send(embed=embed)

    async def translate_detect_lang(self, ctx, input):
        output_lang = await get_lang_code(self, ctx, input[0])
        if output_lang == None:
            return

        text = ' '.join(input[1:])

        output_lang = await get_lang_code(self, ctx, output_lang)
        log.info(f'Output Lang Code: {output_lang}')

        params = {
            'api-version': '3.0',
            'to': output_lang
        }

        body = [{
            'text': text
        }]

        headers = {
            'Ocp-Apim-Subscription-Key': BotSecrets.get_instance().azure_translate_key,
            'Ocp-Apim-Subscription-Region': 'global',
            'Content-type': 'application/json',
            'X-ClientTraceId': TRACE_ID
        }

        async with aiohttp.ClientSession() as session:
            async with await session.post(url=TRANSLATE_API_URL, params=params, headers=headers, json=body) as resp:
                response = json.loads(await resp.text())

        log.info(response[0]['detectedLanguage'])
        log.info(response[0]['translations'])
        embed = discord.Embed(title='Translate', color=Colors.ClemsonOrange)
        name = 'Translated to ' + LANGUAGE_SHORT_CODE_TO_NAME[response[0]['translations'][0]['to'].lower()]
        embed.add_field(name=name, value=response[0]['translations'][0]['text'], inline=False)
        embed.add_field(name='Confidence Level:', value=response[0]['detectedLanguage']['score'], inline=True)
        embed.add_field(name='Detected Language:', value=LANGUAGE_SHORT_CODE_TO_NAME[response[0]['detectedLanguage']['language']], inline=True)
        await ctx.send(embed=embed)
        return


def is_valid_lang_code(input: str):
    return input.lower() in LANGUAGE_SHORT_CODE_TO_NAME or input.lower() in LANGUAGE_NAME_TO_SHORT_CODE


async def get_lang_code(self, ctx, input: str):
    if input.lower() in LANGUAGE_SHORT_CODE_TO_NAME:
        return input.lower()
    else:
        try:
            return LANGUAGE_NAME_TO_SHORT_CODE[input.lower()]
        except KeyError:
            pages = get_language_list(self)
            await self.bot.messenger.publish(Events.on_set_pageable_text,
                                             embed_name='Languages',
                                             field_title='Given language \'' + input + '\' not valid. Here are the available languages:',
                                             pages=pages,
                                             author=ctx.author,
                                             channel=ctx.channel)


def get_language_list(self):
    langs = [f'{name} ({short})' for name, short in LANGUAGE_NAME_TO_SHORT_CODE.items()]
    return ['\n'.join(i) for i in chunk_list(self, langs, CHUNK_SIZE)]


def chunk_list(self, lst, n):
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


def setup(bot):
    bot.add_cog(TranslateCog(bot))
