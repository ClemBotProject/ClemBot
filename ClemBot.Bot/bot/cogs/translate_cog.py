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

TRACE_ID = str(uuid.uuid4())


class TranslateCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @ext.group(case_insensitive=True, invoke_without_command=True)
    @ext.long_help(
        'Allows you to translate words or sentences by specifying an output language and autodetecting the language you entered. Use !translate m for specifying the language you entered. Use \'translate languages\' to see available languages')
    @ext.short_help('Translates words or phrases between two languages')
    @ext.example(('translate es Hello', 'translate german Hello', 'translate languages', 'translate German Como estas?, translate m german english I love partying with german people!'))
    async def translate(self, ctx, *input: str):
        if len(input) < 2:
            raise UserInputError("Incorrect Number of Arguments. Minimum of 2 arguments")

        if (is_valid_lang_code(input[0]) != None):
          await self.translate_given_lang(ctx, input)
        else:
            raise UserInputError("Invalid input! Use !translate m for manual translation.")

    @translate.command(aliases=["manual", "man"])
    @ext.long_help('Alternative command to manually specify languages to convert to.')
    @ext.short_help('!translate m <output lang> <input lang> <text>')
    @ext.example(('!translate m english spanish Me encantan las fiestas con amigos'))
    async def m(self, ctx, *input: str):
        if len(input) < 3:
            raise UserInputError("Incorrect Number of Arguments. Minimum number of 3 arguments")
        if (is_valid_lang_code(input[0]) and is_valid_lang_code(input[1])) != None:
            await self.alternative_translate_lang(ctx, input)
        else:
              raise UserInputError("Invalid input! Specify the language you entered.")

        return

          
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
        output_lang = is_valid_lang_code(input[0])
        text = ' '.join(input[1:])
        params = {
            'api-version': '3.0',
            'to': output_lang
        }

        body = [{
            'text': text
        }]

        headers = {
            'Ocp-Apim-Subscription-Key': bot_secrets.secrets.azure_translate_key,
            'Ocp-Apim-Subscription-Region': 'global',
            'Content-type': 'application/json',
            'X-ClientTraceId': TRACE_ID
        }

        async with aiohttp.ClientSession() as session:
            async with await session.post(url=TRANSLATE_API_URL, params=params, headers=headers, json=body) as resp:
                response = json.loads(await resp.text())
        embed = discord.Embed(title='Translate', color=Colors.ClemsonOrange)
        name = 'Translated to ' + LANGUAGE_SHORT_CODE_TO_NAME[response[0]['translations'][0]['to'].lower()]
        embed.add_field(name=name, value=response[0]['translations'][0]['text'], inline=False)
        await ctx.send(embed=embed)
        return



def is_valid_lang_code(input: str):
        if(input in LANGUAGE_NAME_TO_SHORT_CODE):
            return LANGUAGE_NAME_TO_SHORT_CODE.get(input)
        elif(input in LANGUAGE_SHORT_CODE_TO_NAME):
            return input
        elif(input in LOWERCASE_LANGUAGENAME):
          b = LOWERCASE_LANGUAGENAME.index(input)
          good_list = list(LANGUAGE_SHORT_CODE_TO_NAME)
          return good_list[b]

        elif(input in LOWERCASE_LANGUAGE_SHORT_CODE_TO_NAME):
          g = LOWERCASE_LANGUAGE_SHORT_CODE_TO_NAME.index(input)
          epic_list = list(LANGUAGE_SHORT_CODE_TO_NAME)
          return epic_list[g] 

        elif(input.lower in LOWERCASE_LANGUAGENAME):
            p = input.lower
            g = LOWERCASE_LANGUAGENAME.index(p)
            awesome_list = list(LANGUAGE_SHORT_CODE_TO_NAME)
            return awesome_list[g]

        elif(input.lower in LOWERCASE_LANGUAGE_SHORT_CODE_TO_NAME):
            l = input.lower
            g = LOWERCASE_LANGUAGE_SHORT_CODE_TO_NAME.index(l)
            biggest_list = list(LANGUAGE_SHORT_CODE_TO_NAME)
            return biggest_list[g]
        else: return None
  
    
    
async def alternative_translate_lang(self, ctx, input):
    output_lang = is_valid_lang_code(input[0])
    input_lang = is_valid_lang_code(input[1])
    text = ' '.join(input[2:])       
    params = {
       'api-version': '3.0',
       'from': input_lang,
       'to': output_lang
        }

        body = [{
        'text': text
        }]

        headers = {
        'Ocp-Apim-Subscription-Key': bot_secrets.secrets.azure_translate_key,
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
    return

def is_valid_lang_code(code: str):
    code_lower = code.lower()
    if code_lower in LOWER_CODE_TO_CODE:
        return LOWER_CODE_TO_CODE[code_lower]
    if code_lower in LOWER_LANGUAGE_TO_CODE:
        return LOWER_LANGUAGE_TO_CODE[code_lower]

def get_language_list(self):
    langs = [f'{name} ({short})' for name, short in LANGUAGE_NAME_TO_SHORT_CODE.items()]
    return ['\n'.join(i) for i in chunk_list(self, langs, CHUNK_SIZE)]

    
def chunk_list(self, lst, n):
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
"Bosnian (Latin)":"bs",      
"Bulgarian":"bg",      
"Cantonese (Traditional)":"yue",        
"Catalan":"ca",      
"Chinese (Literary)":"lzh",        
"Chinese Simplified":"zh-Hans",          
"Chinese Traditional":"zh-Hant",          
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
"French (Canada)":"fr-ca",        
"Georgian":"ka",      
"German":"de",      
"Greek":"el",      
"Gujarati":"gu",      
"Haitian Creole":"ht",      
"Hebrew":"he",      
"Hindi":"hi",      
"Hmong Daw":"mww",        
"Hungarian":"hu",      
"Icelandic":"is",      
"Indonesian":"id",      
"Inuinnaqtun":"ikt",        
"Inuktitut":"iu",      
"Inuktitut (Latin)":"iu-Latn",          
"Irish":"ga",      
"Italian":"it",      
"Japanese":"ja",      
"Kannada":"kn",      
"Kazakh":"kk",      
"Khmer":"km",      
"Klingon":"tlh-Lat",          
"Klingon (plqaD)":"tlh-Piq",          
"Korean":"ko",      
"Kurdish (Central)  ":"ku",      
"Kurdish (Northern)":"kmr",        
"Kyrgyz":"ky",      
"Lao":"lo",      
"Latvian":"lv",      
"Lithuanian":"lt",      
"Macedonian":"mk",      
"Malagasy":"mg",      
"Malay ":"ms",      
"Malayalam":"ml",      
"Maltese":"mt",      
"Maori":"mi",      
"Marathi":"mr",      
"Mongolian (Cyrillic)":"mn-Cyrl",          
"Mongolian (Traditional)":"mn-Mong",          
"Myanmar":"my",      
"Nepali":"ne",      
"Norwegian":"nb",      
"Odia":"or",      
"Pashto":"ps",      
"Persian ":"fa",      
"Polish":"pl",      
"Portuguese (Brazil)":"pt",      
"Portuguese (Portugal)":"pt-pt",        
"Punjabi":"pa",      
"Queretaro Otomi":"otq",        
"Romanian":"ro",      
"Russian":"ru",      
"Samoan":"sm",      
"Serbian (Cyrillic)":"sr-Cyrl",          
"Serbian (Latin)":"sr-Latn",          
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
"Upper Sorbian":"hsb",        
"Urdu":"ur",      
"Uyghur":"ug",      
"Uzbek (Latin)":"uz",      
"Vietnamese":"vi",      
"Welsh":"cy",      
"Yucatec Maya":"yua",                           
                         
}

LOWER_LANGUAGE_TO_CODE = {k.lower(): v for k, v in LANGUAGE_NAME_TO_SHORT_CODE.items()}
LOWER_CODE_TO_CODE = {k.lower(): k for k, _ in LANGUAGE_NAME_TO_SHORT_CODE.items()}
CHUNK_SIZE = 15
TRANSLATE_API_URL = "https://api.cognitive.microsofttranslator.com/translate"

def setup(bot):
    bot.add_cog(TranslateCog(bot))