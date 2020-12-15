#This contribution was made by: Rajat Sethi
#Date: 12/15/2020

import logging

import discord
import discord.ext.commands as commands
from bot.messaging.events import Events
from bot.bot_secrets import BotSecrets

import json
import requests


log = logging.getLogger(__name__)

class defineCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.api_key = BotSecrets.get_instance().merriam_key
        self.wordPages = []
    
    def getPageData(self, response, word):
        jsonData = response.json()
        pages = []

        #If the word is found, the JSON will return a dictionary of information. 
        if (isinstance(jsonData[0], dict)):

            #For words with several definitions, it will return several dictionaries. 
            for i in range(len(jsonData)):

                #Current dictionary of information.
                wordData = jsonData[i]

                #Stems of the given word (Past Tense, Future Tense, Perfect Tense, etc.)
                wordStems = []
                try:
                    wordStems = wordData['meta']['stems']
                except:
                    pass
                
                #Syllables of the given word
                syllableData = ""
                try:
                    syllableData = wordData['hwi']['hw']
                except:
                    pass
                
                #Pronunciation of the given word (With those weird letters)
                pronunc = []
                try:
                    prsData = wordData['hwi']['prs']
                    for prs in range(len(prsData)):
                        soundData = prsData[i]
                        pronunc.append(soundData['mw'])

                except:
                    pass
                
                #Type of the given word (Noun, Verb, Adjective, etc.)
                wordType = ""
                try:
                    wordType = wordData['fl']
                except:
                    pass
                
                #Definitions of the given word
                definitions = []
                try:
                    defData = wordData['shortdef']
                    for defin in range(len(defData)):
                        definitions.append(defData[defin])
                except:
                    definitions.append("Definition Missing")
                
                #Turn data into one long string (represents a page)
                template = "Tenses: "
                for s in range(len(wordStems)):
                    template += wordStems[s]
                    if (s != len(wordStems) - 1):
                        template += ", "
                template += "\n"

                template += "Syllables: " + syllableData + "\n"

                template += "Pronunciation: "
                for s in range(len(pronunc)):
                    template += pronunc[s]
                    if (s != len(pronunc) - 1):
                        template += ", "
                template += "\n"

                template += "Word Type: " + wordType + "\n"

                template += "\n"
                for s in range(len(definitions)):
                    page = template + "Definition: " + definitions[s]
                    page = page.replace("*"," | ")
                    pages.append(page)

        #If the word cannot be found, the JSON returns a list of other possible suggestions. 
        elif (isinstance(jsonData[0], str)):
            template = "Word not found, see also: "
            for s in range(len(jsonData)):
                template += jsonData[s]
                if (s != len(jsonData) - 1):
                    template += ", "
    
            pages = [template]

        return pages
    
    @commands.command()
    async def define(self, ctx, word):
        """
        Given a word, find its definition and any other relevant information
        
        USE: !define <word>
        EXAMPLE: !define schadenfreude

        For phrases, use underscores
        EXAMPLE: !define computer_science
        """

        actualWord = word.replace("_"," ")
        word = word.replace("_","%20")
        url = "https://www.dictionaryapi.com/api/v3/references/collegiate/json/" + word.lower() + "?key=" + self.api_key
        response = requests.get(url)
        
        if (response.status_code == 200):
            self.wordPages = self.getPageData(response, word)

        else:
            ErrMsg = "Oh No! There appears to be an issue! Yell at one of the developers with the following code.\nError Code: " + str(response.status_code)
            self.wordPages = [ErrMsg]
        
        await self.bot.messenger.publish(Events.on_set_pageable,
            embed_name = "Merriam-Webster Dictionary",
            field_title = f'Word: {actualWord}',
            pages = self.wordPages,
            author = ctx.author,
            channel = ctx.channel)
    
def setup(bot):
    bot.add_cog(defineCog(bot))


        
