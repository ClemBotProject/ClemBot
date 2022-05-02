import json
import logging
from threading import currentThread
from urllib import response
import uuid
import random
import aiohttp
import discord
import discord.ext.commands as commands
from discord.ext.commands.errors import UserInputError
import bot.bot_secrets as bot_secrets
import bot.extensions as ext
from bot.consts import Colors
from bot.messaging.events import Events








class TriviaCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.session = aiohttp.ClientSession()

    @ext.group(case_insensitive=True, invoke_without_command=True)
    @ext.long.help(
    "Use !trivia to return a random assortment of 10 trivia questions. React with emojis to submit your answer choice"    )
    @ext.short_help(
    "!trivia use !trivia m for custom arguments"    )
    async def Trivia(self, ctx, *input:str):
       async with await self.session.get(url=DEFAULT_URL) as resp:  
            response = json.loads(await resp.text())
            correct_answers = self.JsonParser(response)
            await self.Dict_Publisher(ctx, response)

       return
    @Trivia.command()
    @ext.long_help(
        "Specify arguments you want to return such as question number (max 35), category, difficulty, or question type. Use numbers for quicker specification of category by typing in the number beside the category in !help. Use 0 for unused categories!")
    @ext.short_help("!trivia m <Question Number> <category/substring/number> <Difficulty/Number> <question type>")
    @ext.example(
     "Say you want only bool question types (True/False) and default everything else: !trivia m 10 0 0 2 The only truly required argument is Question Number. You can use 0's for categories you don't want to specify")
    async def manual(self, ctx, *input:str):
     if len(input) < 1:
        raise UserInputError("You need more arguments to use this command")
     FunctionParameters = []   
     for x in range(0, 3):
        FunctionParameters.insert(x, self.Matching_Function(x))    


     url = self.Url_Builder(FunctionParameters)
     async with await self.session.get(url=url) as resp:  
            response = json.loads(await resp.text())
            correct_answers = await self.JsonParser(response)

     return
    async def Url_Builder(self, functionlist):
        url = URL_BUILDER
        for x in range(0,3):
            if functionlist[x] != None:
                    match x:
                        case 0:
                            url = url+ str(functionlist[x])
                        case 1:
                            url = url + "&category="+ str(functionlist[x])
                        case 2: 
                            url = url + "&difficulty=" + functionlist[x]
                        case 3:
                            url = url + "&type="+functionlist[x]             

        return
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
                         Returnthisint = DIFFICULTY_LOWER.index(x)+9
                         return Returnthisint
                     else:
                         raise UserInputError("Difficulty not found")
        case 3:
             if input[3].isnumeric():
                EvaluteInt = int(input[3])
                if 0 < EvaluteInt < 3:
                    finalreturn = QUESTIONTYPE_LOWER[EvaluteInt-1]
                    return finalreturn
                elif EvaluteInt == 0:
                    return None    
             else:
                 questiontype = questiontype.lower()
                 for x in QUESTIONTYPE_LOWER:
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
    async def Json_Parser(dictionary):
        Correct_Answers= []
        for x in dictionary['results']:
            Correct_Answers.append(x['correct_answer'])
        return Correct_Answers

    async def Dict_Publisher(self, ctx, dictionary, Correct_answers):
        x=0
        cog_embeds = []
        List_Index = []
        for bob in dictionary['result']:

         Answers_List= []   
         Answers_List = bob['incorrect_answers']
         Answers_List.append(bob['correct_answer'])
         random.shuffle(Answers_List)
         List_Index.append(Answers_List.index(Correct_answers[bob]))  
         x+=1   
         embed = discord.Embed(title= "Your Trivia Question:",
         descripton="Question #"+x,
         color=Colors.ClemsonOrange)
         embed.addfield(name="Question:", value=bob['question'])
         embed.addfield(name="Category:", value=bob['category'])
         embed.addfield(name="Pick your Answer choice:", inline=False)
         a = 65
         for iterative in Answers_List:

            embed.addfield(name=chr(a)+":", value = iterative, inline=False)
            a=a+1
         cog_embeds.append(embed)
        
        msgembed = await self.bot.messenger.publish(Events.on_set_pageable_embed,
                                         pages=cog_embeds,
                                         author=ctx.author,
                                         channel=ctx.channel,
                                         timeout=360
                                         ) 
        await msgembed.add_reaction('🇦')
        await msgembed.add_reaction('🇧')
        await msgembed.add_reaction('🇨')
        await msgembed.add_reaction('🇩')
        current_pagenumber = 1
        max_pagenumber = len(cog_embeds)
        while not msgembed.empty:
            
         reaction  = await self.client.wait_for("reaction_add", timeout=360, check=check)
         current_pagenumber = await self.On_Reaction(reaction.emoji, List_Index, msgembed, current_pagenumber, max_pagenumber)
        return msgembed
    

    async def On_Reaction(self, ctx, reaction, rightanswer, msgembeds, current_page, max_pagenumber):

            if ANSWER_KEY[rightanswer[current_page]] == reaction:
                del msgembeds[current_page] # Add something to scoreboard to give indication it was right
            elif MOVEMENT_ARROWS.find(reaction):      
                Index_Of = MOVEMENT_ARROWS.index(reaction)
                match Index_Of:
                    case 0:
                        return current_page+1
                    case 1:
                        if current_page > 1:
                            return current_page-1
                    case 2:
                        return max_pagenumber
                    case 3:
                        return 1            
                
            return current_page

    def helper_fixer(formatthis):
         newlist = []
         for x in formatthis:
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

URL_BUILDER = R"https://opentdb.com/api.php?amount="
























DEFAULT_URL = "https://opentdb.com/api.php?amount=10"
   


DIFFICULTY = ["Easy", 
              "Medium", 
              "Hard"]

DIFFICULTY_LOWER = [k.lower() for k in DIFFICULTY]

QUESTIONTYPE = [
    "multiple", 
    "bool"
]
QUESTIONTYPE_LOWER = [k.lower for k in QUESTIONTYPE]
CATEGORYLIST = ["General Knowledge", #Including this out of consistency to avoid making the offset 10 for no reason. This will be the default value.
                 "Books", 
                 "Film", 
                 "Music", 
                 "Musicals & Theatres", 
                 "Television",
                 "Video Games",
                 "Board Games",
                 "Science & Nature", 
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
            "Japanese Anime & Manga",
           "Cartoon & Animations"]
CATEGORYLIST_LOWER = [k.lower for k in CATEGORYLIST]

def setup(bot):
    bot.add_cog(TriviaCog(bot))
    