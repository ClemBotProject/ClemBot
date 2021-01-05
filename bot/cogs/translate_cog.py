import json
import logging
import discord
import aiohttp
import uuid
import bot.extensions as ext
import discord.ext.commands as commands
from discord.ext.commands.errors import UserInputError
from bot.bot_secrets import BotSecrets
from bot.consts import Colors

log = logging.getLogger(__name__)

language_name_to_short_code = {
    "afrikaans": "af",
    "arabic": "ar",
    "bulgarian": "bg",
    "catalan": "ca",
    "chinese simplified": "zh-Hans",
    "chinese traditional":	"zh-Hant",
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
    "kurdish (central)": "ku-Arab",
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
    "serbian (cyrillic)": "sr-Cyrl",
    "serbian (latin)": "sr-Latn",
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

language_short_code_to_name = {value : key for (key, value) in language_name_to_short_code.items()}

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
        self._last_member = None

    @ext.command()
    @ext.long_help('Allows you to translate words or sentences by either specifying both the input and output language with the text to translate, or just the output language and the text to translate')
    @ext.short_help('Translates words or phrases between two languages')
    @ext.example(('translate en spanish Hello', 'translate german Hello'))
    async def translate(self, ctx, *input: str):
        if len(input) < 2:
            raise UserInputError("Incorrect Number of Arguments. Minimum of 2 arguments")
        if is_valid_lang_code(input[1]):
            output_lang = get_lang_code(input[1])
            await self.translate_given_lang(ctx, input)
        else:
            await self.translate_detect_lang(ctx, input)
    
    async def translate_given_lang(self, ctx, input):
        input_lang = input[0]
        output_lang = input[1]
        text = ''
        for i in input[2:]:
            text += f'{i} '

        params = {}

        log.info('Input Lang Code: ' + str(get_lang_code(input_lang)))
        log.info('Output Lang Code: ' + str(get_lang_code(output_lang)))
        params = {
            'api-version': '3.0',
            'from': get_lang_code(input_lang),
            'to': get_lang_code(output_lang)
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
        return
        
    async def translate_detect_lang(self, ctx, input):
        output_lang = input[0]
        text = ''
        for i in input[1:]:
            text += f'{i} '

        log.info('Output Lang Code: ' + str(get_lang_code(output_lang)))
        
        params = {
            'api-version': '3.0',
            'to': get_lang_code(output_lang)
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

def get_lang_code(input: str):
    if input.lower() in language_short_code_to_name:
        return input.lower()
    else: 
        try:
            return language_name_to_short_code[input.lower()]
        except KeyError:
            raise UserInputError('Given language \'' + input + '\' not valid')

def setup(bot): 
    bot.add_cog(TranslateCog(bot))