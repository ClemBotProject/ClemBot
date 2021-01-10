import json
import logging
import discord
import aiohttp
import uuid
import bot.extensions as ext
import discord.ext.commands as commands
from discord.ext.commands.errors import UserInputError
from bot.messaging.events import Events
from bot.bot_secrets import BotSecrets
from bot.consts import Colors

log = logging.getLogger(__name__)

language_name_to_short_code = {
    "afrikaans": "af",
    "arabic": "ar",
    "bulgarian": "bg",
    "catalan": "ca",
    "chinese simplified": "zh-hans",
    "chinese traditional":	"zh-hant",
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
    "hungarian":"hu",
    "icelandic": "is",
    "indonesian": "id",
    "irish": "ga",
    "italian": "it",
    "japanese": "ja",
    "klingon": "tlh-Latn",
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
chunk_size = 15
language_short_code_to_name = {value : key for key, value in language_name_to_short_code.items()}

headers = {
    'Ocp-Apim-Subscription-Key': BotSecrets.get_instance().translator_subscription_key,
    'Ocp-Apim-Subscription-Region': 'global',
    'Content-type': 'application/json',
    'X-ClientTraceId': str(uuid.uuid4())
}


TRANSLATE_API_URL = "https://api.cognitive.microsofttranslator.com/translate"

class TranslateCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @ext.command()
    @ext.long_help('Allows you to translate words or sentences by either specifying both the input and output language with the text to translate, or just the output language and the text to translate')
    @ext.short_help('Translates words or phrases between two languages')
    @ext.example(('translate en spanish Hello', 'translate german Hello'))
    async def translate(self, ctx, *input: str):
        if len(input) < 2:
            raise UserInputError("Incorrect Number of Arguments. Minimum of 2 arguments")
        if is_valid_lang_code(input[1]):
            await self.translate_given_lang(ctx, input)
        else:
            await self.translate_detect_lang(ctx, input)
    
    async def translate_given_lang(self, ctx, input):
        input_lang = await get_lang_code(self, ctx, input[0])
        output_lang = await get_lang_code(self, ctx, input[1])

        if input_lang == None or output_lang == None:
            return

        text = ''.join(input[2:])

        params = {}

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

        async with aiohttp.ClientSession() as session:
            async with await session.post(url = TRANSLATE_API_URL, params = params, headers = headers, json = body) as resp: 
                    response = json.loads(await resp.text())

        log.info(response[0]['translations'])
        embed = discord.Embed(title='Translate', color = Colors.ClemsonOrange)
        name = 'Translated to ' + language_short_code_to_name[response[0]['translations'][0]['to']]
        embed.add_field(name=name, value = response[0]['translations'][0]['text'], inline=False)
        await ctx.send(embed=embed)
        
    async def translate_detect_lang(self, ctx, input):
        output_lang = await get_lang_code(self, ctx, input[0])
        if output_lang == None: 
            return

        text = ''
        for i in input[1:]:
            text += f'{i} '
        output_lang = await get_lang_code(self, ctx, output_lang)
        log.info(f'Output Lang Code: {output_lang}')
        
        params = {
            'api-version': '3.0',
            'to': output_lang
        }
        
        body = [{
            'text': text
        }]
        
        async with aiohttp.ClientSession() as session:
            async with await session.post(url = TRANSLATE_API_URL, params = params, headers = headers, json = body) as resp: 
                response = json.loads(await resp.text())
        
        log.info(response[0]['detectedLanguage'])
        log.info(response[0]['translations'])
        embed = discord.Embed(title='Translate', color = Colors.ClemsonOrange)
        name = 'Translated to ' + language_short_code_to_name[response[0]['translations'][0]['to']]
        embed.add_field(name=name, value = response[0]['translations'][0]['text'], inline=False)
        embed.add_field(name='Confidence Level:', value = response[0]['detectedLanguage']['score'], inline=True)
        embed.add_field(name='Detected Language:', value = language_short_code_to_name[response[0]['detectedLanguage']['language']], inline=True)
        await ctx.send(embed=embed)
        return

def is_valid_lang_code(input: str):
    return input.lower() in language_short_code_to_name or input.lower() in language_name_to_short_code

async def get_lang_code(self, ctx, input: str):
    if input.lower() in language_short_code_to_name:
        return input.lower()
    else: 
        try:
            return language_name_to_short_code[input.lower()]
        except KeyError:
            pages = get_language_list()
            await self.bot.messenger.publish(Events.on_set_pageable_text,
                embed_name='Languages',
                field_title='Given language \'' + input + '\' not valid. Here are the available languages:',
                pages = pages,
                author=ctx.author,
                channel=ctx.channel)

def get_language_list():
    languages_dict = []
    for i in range(0, len(language_name_to_short_code)):
        languages_dict.append(list(language_name_to_short_code)[i] + ' (' + language_name_to_short_code[list(language_name_to_short_code)[i]] + ')')
    pages = []
    for i in range(0, len(languages_dict), chunk_size):
        pages.append('\n'.join(languages_dict[i:i+chunk_size]))
    return pages

def setup(bot): 
    bot.add_cog(TranslateCog(bot))