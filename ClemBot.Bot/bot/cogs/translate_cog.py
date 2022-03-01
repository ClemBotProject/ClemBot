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
import bot.language_consts

log = logging.getLogger(__name__)

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

        if (is_valid_lang_code(input[0])) != None):
          await self.translate_given_lang(self, ctx, input)
        else:
            raise UserInputError("Incorrect")

        @translate.command()
        @ext.long_help('Shows all available languages to translate between')
        @ext.short_help('Shows available languages')
        @ext.example(('translate languages'))

    async def translatem(self, ctx, *input: str):
        if len(input) < 2:
            raise UserInputError("Incorrect Number of Arguments. Minimum of 2 arguments")
        if (is_valid_lang_code(input[0]) and is_valid_lang_code(input[1])) != None:
            await alternative_translate_lang(self, ctx, input)
            else:
                raise UserInputError("Incorrect")
            @translatem.command()
            @ext.long_help('Manual Translator')
            @ext.short_help('Translator with 2 args')
            @ext.example('translate')

    async def languages(self, ctx):
        await self.bot.messenger.publish(Events.on_set_pageable_text,
                                         embed_name='Languages',
                                         field_title='Here are the available languages:',
                                         pages=get_language_list(self),
                                         author=ctx.author,
                                         channel=ctx.channel)
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


    async def translate_given_lang(self, ctx, input):
        output_lang = await is_valid_lang_code(input[0])
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

        log.info(response[0]['translations'])
        embed = discord.Embed(title='Translate', color=Colors.ClemsonOrange)
        name = 'Translated to ' + LANGUAGE_SHORT_CODE_TO_NAME[response[0]['translations'][0]['to'].lower()]
        embed.add_field(name=name, value=response[0]['translations'][0]['text'], inline=False)
        await ctx.send(embed=embed)
        return


  
    
    
async def alternative_translate_lang(self, ctx, input):
    output_lang = await is_valid_lang_code(input[0]) 
    input_lang = await is_valid_lang_code(input[1])
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





    
def get_language_list(self):
            langs = [f'{name} ({short})' for name, short in LANGUAGE_NAME_TO_SHORT_CODE.items()]
            return ['\n'.join(i) for i in chunk_list(self, langs, CHUNK_SIZE)]
    
def chunk_list(self, lst, n):
      for i in range(0, len(lst), n):
        yield lst[i:i + n]


def setup(bot):
    bot.add_cog(TranslateCog(bot))

