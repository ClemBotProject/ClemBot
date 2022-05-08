import json
import logging
import uuid
import aiohttp
import discord
import discord.ext.commands as commands
from discord.ext.commands.errors import UserInputError
import bot.bot_secrets as bot_secrets
import bot.extensions as ext
from bot.consts import Colors
from bot.messaging.events import Events

log = logging.getLogger(__name__)

class TranslateCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.session = aiohttp.ClientSession()

    @ext.group(case_insensitive=True, invoke_without_command=True)
    @ext.long_help(
        'Allows you to translate words or sentences by entering an output language and autodetecting the language you input. run \'translate languages\' to see available languages')
    @ext.short_help('Translates words or phrases using autodetect.')
    @ext.example(('translate spanish Hello', 'translate german Hello', 'translate languages', 'translate German Como estas?', "!translate <outputlang> <text>"))
    async def translate(self, ctx, *input: str):

        if len(input) < 2:
            raise UserInputError("Incorrect Number of Arguments. Minimum of 2 arguments")
        
        languagecode = await get_lang_code(input[0])
        if languagecode:
            await self.translate_given_lang(ctx, languagecode, input)
        else:
            await self.error_handling(ctx, languagecode)
            

    @translate.command()
    @ext.long_help('Shows all available languages to translate between')
    @ext.short_help('Shows available languages')
    @ext.example(('translate languages'))
    async def languages(self, ctx):

        await self.bot.messenger.publish(Events.on_set_pageable_text,
                                         embed_name='Languages',
                                         field_title='Here are the available languages:',
                                         pages=get_language_list(),
                                         author=ctx.author,
                                         channel=ctx.channel)
        return
    @translate.command(aliases=['m'])
    @ext.long_help('Manually specifies an input langauge !translate m <outputlang> <input language> <text>')
    @ext.short_help('Specify an output language + the language you entered to translate')
    @ext.example('translate m or translate manual')
    async def manual(self, ctx, *input: str):

        output_lang = await get_lang_code(input[0])
        input_lang = await get_lang_code(input[1])
        if output_lang and input_lang:

         text = ' '.join(input[2:])

         params = {
             'api-version': '3.0',
             'from': input_lang,
             'to': output_lang
         }

         body = [{
             'text': text
         }]

         async with await self.session.post(url=TRANSLATE_API_URL, params=params, headers=HEADERS, json=body) as resp:
             response = json.loads(await resp.text())

         embed = discord.Embed(title='Translate', color=Colors.ClemsonOrange)
         name = 'Translated to ' + LANGUAGE_SHORT_CODE_TO_NAME[response[0]['translations'][0]['to']]
         embed.add_field(name=name, value=response[0]['translations'][0]['text'], inline=False)
         await ctx.send(embed=embed)
         return
        else:
           await self.error_handling(ctx, output_lang)
           return

    async def error_handling(self, ctx, error: str):

        if not error:   #Double making sure that the string isn't actually set so this doesn't get published multiple times.
              await self.bot.messenger.publish(Events.on_set_pageable_text,
                                                embed_name='Languages',
                                                field_title='Language entry is not valid. Here are the available languages:',
                                                pages=get_language_list(),
                                                author=ctx.author,
                                                channel=ctx.channel)

        



    async def translate_given_lang(self, ctx, language: str, input):

        output_lang = language
        text = ' '.join(input[1:])

        params = {
            'api-version': '3.0',
            'to': output_lang
        }

        body = [{
            'text': text
        }]
        
        async with await self.session.post(url=TRANSLATE_API_URL, params=params, headers=HEADERS, json=body) as resp:
            response = json.loads(await resp.text())

        embed = discord.Embed(title='Translate', color=Colors.ClemsonOrange)
        name = 'Translated from: ' + LANGUAGE_SHORT_CODE_TO_NAME[response[0]['detectedLanguage']['language']]
        embed.add_field(name='Confidence Level:', value=response[0]['detectedLanguage']['score'], inline=True)
        embed.add_field(name=name, value=response[0]['translations'][0]['text'], inline=False)
        await ctx.send(embed=embed)
        return
    
    def cog_unload(self):
        self.session.close()



async def get_lang_code(language: str):
    
    language_lower = language.lower()
    if language_lower in LOWER_LANGUAGE_TO_CODE:
        return LOWER_LANGUAGE_TO_CODE[language_lower]
    elif language_lower in LOWER_CODE_TO_CODE:
        return LOWER_CODE_TO_CODE[language_lower]


def get_language_list():

    langs = [f'{name} ({short})' for name, short in LANGUAGE_NAME_TO_SHORT_CODE.items()]
    return ['\n'.join(i) for i in chunk_list(langs, CHUNK_SIZE)]


def chunk_list(lst, n):

    for i in range(0, len(lst), n):
        yield lst[i:i + n]
        

LANGUAGE_NAME_TO_SHORT_CODE = {
            "Afrikaans":"af",      
            "Albanian":"sq",      
            "Amharic":"am",      
            "Arabic":"ar",      
            "Armenian":"hy",      
            "Assamese":"as",      
            "Azerbaijani":"az",      
            "Bangla":"bn",      
            "Bashkir":"ba",      
            "Bosnian-Latin":"bs",      
            "Bulgarian":"bg",      
            "Cantonese-Traditional":"yue",        
            "Catalan":"ca",      
            "Chinese-Literary":"lzh",        
            "Chinese-Simplified":"zh-Hans",          
            "Chinese-Traditional":"zh-Hant",          
            "Croatian":"hr",      
            "Czech":"cs",      
            "Danish":"da",      
            "Dari":"prs",        
            "Divehi":"dv",      
            "Dutch":"nl",      
            "English":"en",      
            "Estonian":"et",      
            "Fijian":"fj",      
            "Filipino":"fil",        
            "Finnish":"fi",      
            "French":"fr",      
            "French-Canada":"fr-ca",        
            "Georgian":"ka",      
            "German":"de",      
            "Greek":"el",      
            "Gujarati":"gu",      
            "Haitian-Creole":"ht",      
            "Hebrew":"he",      
            "Hindi":"hi",      
            "Hmong-Daw":"mww",        
            "Hungarian":"hu",      
            "Icelandic":"is",      
            "Indonesian":"id",      
            "Inuinnaqtun":"ikt",        
            "Inuktitut":"iu",      
            "Inuktitut-Latin":"iu-Latn",          
            "Irish":"ga",      
            "Italian":"it",      
            "Japanese":"ja",      
            "Kannada":"kn",      
            "Kazakh":"kk",      
            "Khmer":"km",      
            "Klingon":"tlh-Lat",          
            "Klingon-plqaD":"tlh-Piq",          
            "Korean":"ko",      
            "Kurdish-Central":"ku",      
            "Kurdish-Northern":"kmr",        
            "Kyrgyz":"ky",      
            "Lao":"lo",      
            "Latvian":"lv",      
            "Lithuanian":"lt",      
            "Macedonian":"mk",      
            "Malagasy":"mg",      
            "Malay":"ms",      
            "Malayalam":"ml",      
            "Maltese":"mt",      
            "Maori":"mi",      
            "Marathi":"mr",      
            "Mongolian-Cyrillic":"mn-Cyrl",          
            "Mongolian-Traditional":"mn-Mong",          
            "Myanmar":"my",      
            "Nepali":"ne",      
            "Norwegian":"nb",      
            "Odia":"or",      
            "Pashto":"ps",      
            "Persian ":"fa",      
            "Polish":"pl",      
            "Portuguese-Brazil":"pt",      
            "Portuguese-Portugal":"pt-pt",        
            "Punjabi":"pa",      
            "Queretaro Otomi":"otq",        
            "Romanian":"ro",      
            "Russian":"ru",      
            "Samoan":"sm",      
            "Serbian-Cyrillic":"sr-Cyrl",          
            "Serbian-Latin":"sr-Latn",          
            "Slovak":"sk",      
            "Slovenian":"sl",      
            "Spanish":"es",      
            "Swahili":"sw",      
            "Swedish":"sv",      
            "Tahitian":"ty",      
            "Tamil":"ta",      
            "Tatar":"tt",      
            "Telugu":"te",      
            "Thai":"th",      
            "Tibetan":"bo",      
            "Tigrinya":"ti",      
            "Tongan":"to",      
            "Turkish":"tr",      
            "Turkmen":"tk",      
            "Ukrainian":"uk",      
            "Upper-Sorbian":"hsb",        
            "Urdu":"ur",      
            "Uyghur":"ug",      
            "Uzbek-Latin":"uz",      
            "Vietnamese":"vi",      
            "Welsh":"cy",      
            "Yucatec-Maya":"yua",                           
                         
}
CHUNK_SIZE = 15
LOWER_LANGUAGE_TO_CODE = {k.lower(): v for k, v in LANGUAGE_NAME_TO_SHORT_CODE.items()}
LOWER_CODE_TO_CODE = {x.lower():x for x,x in LANGUAGE_NAME_TO_SHORT_CODE.items()}
LANGUAGE_SHORT_CODE_TO_NAME = {value: key for key, value in LANGUAGE_NAME_TO_SHORT_CODE.items()}
TRANSLATE_API_URL = "https://api.cognitive.microsofttranslator.com/translate"


HEADERS = {
            'Ocp-Apim-Subscription-Key': bot_secrets.secrets.azure_translate_key,
            'Ocp-Apim-Subscription-Region': 'global',
            'Content-type': 'application/json',
            'X-ClientTraceId': str(uuid.uuid4())
        }


def setup(bot):
    bot.add_cog(TranslateCog(bot))
