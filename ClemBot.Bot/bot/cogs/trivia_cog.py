import json
import logging
import threading
from urllib import response
import uuid
import random
import aiohttp
import asyncio
import discord
import discord.ext.commands as commands
from discord.ext.commands.errors import UserInputError
import bot.bot_secrets as bot_secrets
import bot.extensions as ext
from bot.consts import Colors
from bot.messaging.events import Events







class TriviaCog(commands.Cog):
    def cog_unload(self):
            self.session.close() 
    def __init__(self, bot):
        self.bot = bot
        self.session = aiohttp.ClientSession(headers={'Connection': 'keep-alive'})
        

    @ext.group(case_insensitive=True, invoke_without_command=True)
    @ext.long_help(
    "Use !trivia to return a random assortment of 10 trivia questions. React with emojis to submit your answer choice"    )
    @ext.short_help(
    "!trivia use !trivia m for custom arguments"    )
    async def Trivia(self, ctx):
        async with await self.session.get(DEFAULT_URL) as resp:
                theresponse = json.loads(await resp.text())
                correct_answers = await self.Json_Parser(ctx, theresponse)
             
        dictreturn = await self.Dict_Publisher(ctx, theresponse, correct_answers)                  
                       
    @Trivia.command(aliases=['m'])
    @ext.long_help(
        "Specify arguments you want to return such as question number (max 35), category, difficulty, or question type. Use numbers for quicker specification of category by typing in the number beside the category in !help. Use 0 for unused categories!")
    @ext.short_help("!trivia m <Question Number> <category/substring/number> <Difficulty/Number> <question type>")
    @ext.example(
     "Say you want only bool question types (True/False) and default everything else: !trivia m 10 0 0 2 The only truly required argument is Question Number. You can use 0's for categories you don't want to specify")
    async def manual(self, ctx, *input:str):
     if len(input) < 1:
        raise UserInputError("You need more arguments to use this command")
     FunctionParameters = []
     inputlength = len(input)
     x=0
     while x < inputlength:
        
        appendthis = await self.Matching_Function(x, *input)
        print(appendthis)
        FunctionParameters.append(appendthis)
        x+=1    
     url = await self.Url_Builder(FunctionParameters, inputlength)
     print(url)
     async with await self.session.get(url) as resp:  
            response = json.loads(await resp.text())
            correct_answers = await self.Json_Parser(ctx, response)
     if response['response_code'] == 1:
         raise Exception(
                            "There isn't enough questions in that category. Lower your question amount or select another! Or select a different question type!")


     theembed = await self.Dict_Publisher(ctx, response, correct_answers)       

     return
    async def Url_Builder(self, functionlist, inputlength):
            max_index = inputlength-1
            url = URL_BUILDER+ str(functionlist[0])
            for x in range(1, max_index):
                if functionlist[x]:
                     match x:
                         case 1:
                                 url+=("&category="+ str(functionlist[1]))
                         case 2: 
                                url+=("&difficulty=" + functionlist[2])
                         case 3:
                                 url+=("&type="+functionlist[max_index])
            return url   
                          
          
            
    async def Matching_Function(self, case, *input:str):
     
     match case:
        case 0:
            if input[0].isnumeric():
                questionnumber = int(input[0])
                if 0 < questionnumber <= 50:
                    return questionnumber    

            else:
                raise UserInputError("Question Number has to be a number within the range of 1 to 50")
                     
            
        case 1:
            if input[1].isnumeric():
                trivianumber = int(input[1])
                if 0 < trivianumber <= 24:
                    return trivianumber+8
                elif trivianumber == 0:
                    return None    

            else:
                triviacategory = input[1].lower()
                for x in CATEGORYLIST_LOWER:
                 if x.find(triviacategory) != -1:
                     Returnthis = CATEGORYLIST_LOWER.index(x)+9
                     return Returnthis
                else:
                     raise UserInputError("Category not found!")     
        case 2:                         
            if input[2].isnumeric():
                EvaluteInt = int(input[2])
                if 0 < EvaluteInt <= 3:
                    ReturnString = DIFFICULTY_LOWER[EvaluteInt-1]
                    return ReturnString
                elif EvaluteInt==0:
                    return None    
        
            else: 
                 difficulty = input[2].lower()
                 for x in DIFFICULTY_LOWER:
                     if(x.find(difficulty) != -1):
                         return x
                 else:
                         raise UserInputError("Difficulty not found")
        case 3:
             if input[3].isnumeric():
                EvaluteInt = int(input[3])
                if 0 < EvaluteInt < 3:
                    finalreturn = QUESTIONTYPE[EvaluteInt-1]
                    return finalreturn
                elif EvaluteInt == 0:
                    return None    
             else:
                 questiontype = input[3].lower()
                 for x in QUESTIONTYPE:
                    if(x.find(questiontype) != -1):
                     return x 
                 else:
                        raise UserInputError("Question type invalid.")    
     return                      
    async def List_Help(self):
        embed_list = []
        embed_list.append(self.helper_fixer(CATEGORYLIST))
        embed_list.append(self.helper_fixer(DIFFICULTY))
        embed_list.append(self.helper_fixer(QUESTIONTYPE))
        embed = discord.Embed(title= "Help Page:",
         descripton="Help Page:",
         color=Colors.ClemsonOrange)
        embed.addfield(name="Categories:", value=CATEGORYLIST)
         
        return
    async def Json_Parser(self,ctx, dictionary):
        Correct_Answers= []
        for x in dictionary['results']:
            Correct_Answers.append(x['correct_answer'])
        return Correct_Answers

    async def Dict_Publisher(self, ctx, dictionary, Correct_answers):
        x=0
        cog_embeds = []
        List_Index = []
        for bob in dictionary['results']:
             Answers_List= []   
             Answers_List = bob['incorrect_answers']
             Answers_List.append(bob['correct_answer'])
             Right_Answer = bob['correct_answer']
             random.shuffle(Answers_List)
             List_Index.append(Answers_List.index(Right_Answer))  
             x+=1   
             embed = discord.Embed(title= "Your Trivia Question #"+str(x)+":",
             color=Colors.ClemsonOrange)
             embed.add_field(name="Question:", value=bob['question'])
             embed.add_field(name="Category:", value=bob['category'])
             a = 65
             for iterative in Answers_List:

                embed.add_field(name="Answer Choice  "+chr(a)+" :", value = iterative, inline=False)
                a=a+1
             cog_embeds.append(embed)
          
        
        
       
        
        await self.bot.messenger.publish(Events.on_set_pageable_embed,
                                         pages=cog_embeds,
                                         author=ctx.author,
                                         channel=ctx.channel,
                                         timeout=360,
                                        )
                                        
        tester = discord.ext.commands.Paginator.pages                           
       
                                      
                                                                       
        print("yes\n\n\n\n\n")
        def newcheck(bot):
            return bot.author == self.bot.user.id
        msg = await self.bot.wait_for("message", check=newcheck)                                                                   
       # await msgembed.add_reaction('🇦')
       # await msgembed.add_reaction('🇧')
       # await msgembed.add_reaction('🇨')
        #await msgembed.add_reaction('🇩')
       
        def check(reaction, user):
            return user == ctx.author and ANSWER_KEY.find(str(reaction.emoji)) != -1
            
            
        while Publish_Embed.is_alive():
            
                reaction, user  = await self.client.wait_for("reaction_add", timeout=360, check=check)
                current_pagenumber = discord.ext.pages.Paginator.current_page
        
        return                                                                          
        
    
   
    async def On_Reaction(self, ctx, reaction, rightanswer, msgembeds, current_page, max_pagenumber):

            if ANSWER_KEY[rightanswer[current_page]] == reaction:
                del msgembeds[current_page] # Add something to scoreboard to give indication it was right
          
                
            return
   

    def helper_fixer(formatthis):
         newlist = []
         for x in formatthis:   #Fix this+ formatting
           newlist[x] = '\n'.append(formatthis[x]) + "     Index Of Element:"+formatthis.index([x])
         for i in range(0, len(formatthis), CHUNK_SIZE):
             yield newlist[i:i+CHUNK_SIZE]          

CHUNK_SIZE = 15

ANSWER_KEY=['🇦',
            '🇧',
            '🇨',
            '🇩']
             
MOVEMENT_ARROWS=['➡️',
                '⬅️',
               '⏭️',
               '⏮️' ]

CATEGORY_OFFSET = 9
URL_PARAMS = {
    "amount":"10",
    "category":"",
    "difficulty":"",
    "type":""
}

URL_BUILDER = R"https://opentdb.com/api.php?amount="
























DEFAULT_URL = "https://opentdb.com/api.php?amount=10"
   


DIFFICULTY = ["Easy", 
              "Medium", 
              "Hard"]

DIFFICULTY_LOWER = [k.lower() for k in DIFFICULTY]

QUESTIONTYPE = [
    "multiple", 
    "boolean"
]
CATEGORYLIST = ["General-Knowledge", #Including this out of consistency to avoid making the offset 10 for no reason. This will be the default value.
                 "Books", 
                 "Film", 
                 "Music", 
                 "Musicals&Theatres", 
                 "Television",
                 "Video-Games",
                 "Board-Games",
                 "Science&Nature", 
                 "Computers", 
                 "Mathematics", 
                 "Mythology", 
                 "Sports", 
                 "Geography", 
                 "History", 
                 "Politics", 
                 "Art",
                "Celebrities",
               "Animals", 
               "Vehicles",
              "Comics",
             "Gadgets",
            "Japanese-Anime&Manga",
           "Cartoon&Animations"]
CATEGORYLIST_LOWER = [k.lower() for k in CATEGORYLIST]

def setup(bot):
    bot.add_cog(TriviaCog(bot))
    