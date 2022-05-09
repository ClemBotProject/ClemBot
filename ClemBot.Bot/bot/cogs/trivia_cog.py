import json
import logging
import uuid
import random
import aiohttp
import html
import asyncio
import typing as t
from dataclasses import dataclass
import discord
import discord.ext.commands as commands
from discord.ext.commands.errors import UserInputError
import bot.bot_secrets as bot_secrets
import bot.extensions as ext
from bot.consts import Colors
from bot.messaging.events import Events
log = logging.getLogger(__name__)
    
        
    
class TriviaCog(commands.Cog):
    

            def cog_unload(self):
    
                    self.session.close() 
    
            def __init__(self, bot):
                self.messages = {}
                self.bot = bot
                self.session = aiohttp.ClientSession(headers={'Connection': 'keep-alive'})
                
            @ext.group(case_insensitive=True, invoke_without_command=True)
            @ext.long_help(
            "Use !trivia to return a random assortment of 10 trivia questions. React with emojis to submit your answer choice"    )
            @commands.cooldown(1, 25, commands.BucketType.user)
            @ext.short_help(
            "!trivia use !trivia m for custom arguments"    )
            async def trivia(self, ctx):
                
                async with await self.session.get(DEFAULT_URL) as resp:
    
                        parse_text = await resp.text()
                        new_response = json.loads(parse_text)
                        parsed_response = await self.HTML_Parser(new_response)                
    
                        #If you're curious as to why this doesn't check response code: It's because it will never NOT have questions for the default. If it does the website is down and it will error out anyway.
              
                
                best_list = await self.Dict_Publisher(parsed_response)
                
               
                newtask = await self.Asyncio_Publisher(ctx, best_list[1]) #this will return None when completed ending the loop
    
                thereaction = asyncio.create_task(
                   self.On_Reaction(ctx, newtask[3]))
                
                task1 = asyncio.create_task(self.send_scroll_reactions(newtask[0], newtask[1], newtask[2]))
    
                user_reaction = await thereaction
    
                await self.Parse_Reaction(newtask[0],user_reaction[0],user_reaction[1], best_list[0])
                
                while not task1.done():
    
                    New_reaction = asyncio.create_task(
                    self.On_Reaction(ctx, newtask[3]))
    
                    new_reaction = await New_reaction
                    await self.Parse_Reaction(newtask[0],new_reaction[0], new_reaction[1], best_list[0])    
    
                return                  
                               
            @trivia.command(aliases=['m'])
            @ext.long_help(
                "Specify arguments you want to return such as question number (max 35), category, difficulty, or question type. Use numbers for quicker specification of category by typing in the number beside the category in !help. Use 0 for unused categories!")
            @ext.short_help("!trivia m <Question Number> <category/substring/number> <Difficulty/Number> <question type>")
            @commands.cooldown(1, 40, commands.BucketType.user)
            @ext.example(
             "Say you want only bool question types (True/False) and default everything else: !trivia m 10 0 0 2 The only truly required argument is Question Number. You can use 0's for categories you don't want to specify")
            async def manual(self, ctx, *input:str):
             if len(input) < 1 or 4 < len(input):
                raise UserInputError("Invalid arguments! Specify between 1 to 4")
    
             FunctionParameters = []
             inputlength = len(input)
             x=0
    
             while x < inputlength:
                
                appendthis = await self.Matching_Function(x, *input)
                FunctionParameters.append(appendthis)
                x+=1  
    
             url = await self.Url_Builder(FunctionParameters, inputlength)
    
             async with await self.session.get(url) as resp:  
                    response = json.loads(await resp.text())
    
             if response['response_code'] == 1:
                 raise Exception(
                                "There isn't enough questions in that category. Lower your question amount or select another! Or select a different question type!")
    
             parsed_response = await self.HTML_Parser(response)
    
             big_list = await self.Dict_Publisher(parsed_response)
             
    
             newtask = await self.Asyncio_Publisher(ctx, big_list[1])
    
             thereaction = asyncio.create_task(
                   self.On_Reaction(ctx, newtask[3])
               )
    
             task1 = asyncio.create_task(self.send_scroll_reactions(newtask[0], newtask[1], newtask[2]))
    
             reaction = await thereaction
    
             await self.Parse_Reaction(newtask[0],reaction[0],reaction[1], big_list[0])
    
             while not task1.done():
                new_reaction = asyncio.create_task(
                        self.On_Reaction(ctx, newtask[3]))
    
                use_reaction = await new_reaction
    
                await self.Parse_Reaction(newtask[0],use_reaction[0],use_reaction[1], big_list[0])
      
             return
    
            @trivia.command(aliases=['help'])
            @ext.long_help(
                            "Lists the categories, difficulty, and type of questions. Useful for finding the index of categories!")
            @ext.short_help(
                        "Use this to find the category you want!" ) 
            @commands.cooldown(1, 30, commands.BucketType.user)                
            @ext.example("!trivia help" )                        
            async def List_Help(self, ctx):
    
                embed_list = []
                Final_Page = []
    
                Category_Generator = helper_fixer(CATEGORYLIST)
                for x in Category_Generator:
    
                    embed_list.append(x)
    
                sizeofcategory = len(embed_list)
                x = 0
    
                while x < sizeofcategory:
    
                    Category_embed = discord.Embed(title="Category List:", color = Colors.ClemsonOrange)
                    Category_embed.add_field(name="Index:",value=embed_list[x])
    
                    Final_Page.append(Category_embed)
                    x+=1
    
                Difficulty_Generator = helper_fixer(DIFFICULTY)
    
                for i in Difficulty_Generator:
    
                    embed_list.append(i)
    
                new_insertion = len(embed_list)
    
                while sizeofcategory < new_insertion:
    
                    Difficulty_embed = discord.Embed(title="Difficulty List:", color = Colors.ClemsonOrange)
                    Difficulty_embed.add_field(name="Index:",value=embed_list[sizeofcategory])
    
                    Final_Page.append(Difficulty_embed)
                    sizeofcategory+=1
    
                Question_Generator = helper_fixer(QUESTIONTYPE)
    
                for i in Question_Generator:
                    embed_list.append(i)
    
                last_size = len(embed_list)
                while new_insertion < last_size:
    
                    Type_embed = discord.Embed(title="Question Type:", color = Colors.ClemsonOrange)
                    Type_embed.add_field(name="Index:",value=embed_list[new_insertion])
    
                    Final_Page.append(Type_embed)
                    new_insertion+=1 
    
                await self.bot.messenger.publish(Events.on_set_pageable_embed,
                                                 pages=Final_Page,
                                                 author=ctx.author,
                                                 channel=ctx.channel,
                                                 timeout=60,)
               
                 
                return 
    
    
            async def Url_Builder(self, functionlist, inputlength):
    
                    max_index = inputlength-1
                    url = URL_BUILDER+ str(functionlist[0])
                    x = 1
    
                    while x <= max_index:
                         if functionlist[x]:
                             match x:
                                 case 1:
                                         url+=("&category="+ str(functionlist[1]))
                                 case 2: 
                                        url+=("&difficulty=" + functionlist[2])
                                 case 3:
                                         url+=("&type="+functionlist[max_index])
                         x+=1  
    
                    return url   
    
    
            async def Matching_Function(self, case, *input:str):
             
             match case:       #Revolves around beautiful O(1) based indexing
                case 0:
                    if input[0].isnumeric():
    
                        questionnumber = int(input[0])
    
                        if 0 < questionnumber <= 50:
    
                            return questionnumber    
    
                    else:
                        raise UserInputError(
                            "Question Number has to be a number within the range of 1 to 50")
                             
                    
                case 1:
                    if input[1].isnumeric():
    
                        trivianumber = int(input[1])
    
                        if 0 < trivianumber <= 24:
    
                            return trivianumber+8
    
                        elif trivianumber == 0:
    
                            return None 
                        else:
                            raise UserInputError(
                                        "Category Number out of bounds(Number has to be 1-24) or enter the category you want! Type ?trivia help to see the category list")       
    
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
                            raise UserInputError(
                                "Difficulty Number out of bounds(Number has to be 1-3) or enter Easy-Hard! Type ?trivia help to see the difficulty list.")
    
                
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
                            raise UserInputError(
                                    "Question type number out of bounds(1 or 2) 1: Multiple Choice 2: Boolean. Type ?trivia help to see our question types.")        
                     else:
                         questiontype = input[3].lower()
    
                         for x in QUESTIONTYPE:
    
                            if(x.find(questiontype) != -1):
                             return x 
                         else:
                                raise UserInputError(
                                    "Couldn't find the question type you are looking for!.")    
             return    
            
    
            async def HTML_Parser(self, new_response):
    
                        dictionary_list = [] #pain
    
                        for x in new_response['results']:
    
                          new_dictionary = x
                          new_list_values = x.values()
                          proper_values = []
    
                          for b in new_list_values:
    
                              if isinstance(b, list):
    
                                    new_list = []
    
                                    for y in b:
    
                                      if not y.isnumeric():
                                         new_list.append(html.unescape(y)) #This HTML response is in a weird format where you have to navigate a list that contains dictionaries with that dictionary containing a SINGLE list
                                      else:
                                          new_list.append(y)
    
                                    proper_values.append(new_list)             
                                          
                              elif not b.isnumeric():
    
                                  proper_values.append(html.unescape(b))  # good luck maintaining this 
                              else:
                                  proper_values.append(b)
    
                          propervalues_size = len(proper_values)        
                          biggest_loop = 0   
    
                          for key, value in new_dictionary.items(): #.items is special because it contains an active view 
    
                                new_dictionary[key] = proper_values[biggest_loop]
                                if biggest_loop < propervalues_size:
                                    biggest_loop+=1
                                else:
                                    break  
    
                          dictionary_list.append(new_dictionary)
    
                        dictionarysize = len(new_response['results'])
                        best_loopint = 0  
    
                        while best_loopint < dictionarysize:
    
                              new_response['results'][best_loopint] = dictionary_list[best_loopint] 
                              best_loopint+=1
    
                        return new_response
    
    
            async def Dict_Publisher(self, dictionary):
    
                x=0
                cog_embeds = []
                List_Index = []
    
                for create_lists in dictionary['results']:
    
                     Answers_List= []   
                     Answers_List = create_lists['incorrect_answers']
                     Answers_List.append(create_lists['correct_answer'])
                     Right_Answer = create_lists['correct_answer']
    
                     random.shuffle(Answers_List)
                     List_Index.append(Answers_List.index(Right_Answer))  
                     x+=1   
                     embed = discord.Embed(title= "Question #"+str(x)+":",
                     color=Colors.ClemsonOrange)
    
                     embed.add_field(name="Question:", value=create_lists['question'])
                     embed.add_field(name="Category:", value=create_lists['category'])
    
                     a = 65
                     for iterative in Answers_List:
    
                        embed.add_field(name="Answer Choice  "+chr(a)+" :", value = iterative, inline=False)
                        a=a+1
    
                     cog_embeds.append(embed)
    
                mega_list=[]
                mega_list.append(List_Index)
                mega_list.append(cog_embeds)
    
                return mega_list                                                                    
            async def Asyncio_Publisher(self,ctx, cog_embeds):
    
                Coroutine_Object = await self.set_embed_pageable(cog_embeds, ctx.author, ctx.channel, len(cog_embeds)*9)
                return Coroutine_Object                                    
                
            async def On_Reaction(self,ctx, message):
                author = ctx.author
    
                def check(reaction, user):
                    return user == author and reaction.message.id == message 
    
                reaction, user = await self.bot.wait_for("reaction_add", check=check)
    
                Return_list = []
                Return_list.append(reaction) #Returning this 
                Return_list.append(user)
    
                return Return_list
                      
            async def Parse_Reaction(self, message, reaction,user, right_answer):
                
                msg = self.messages[reaction.message.id]
                current_page = msg.curr_page_num #If you actually refrence msg.curr_page_num every time it performs a lookup -> to the class rather than a constant 
                match reaction.emoji:
                    case '🇦':
                        if right_answer[current_page] == ANSWER_KEY.index('🇦'): # parsing reactions with match case because it is slightly quicker
                            print("It's right")
    
                    case '🇧':
                        if right_answer[current_page] == ANSWER_KEY.index('🇧'):
                            print("It's right")
    
                    case '🇨':
                        if right_answer[current_page] == ANSWER_KEY.index('🇨'):
                            print("It's right")   
    
                    case '🇩':
                        if right_answer[current_page] ==  ANSWER_KEY.index('🇩'):
                            print("It's right")   
    
    
                if len(msg.pages) <= 1:
    
                    await message.delete()
    
                    return
                else:
                    del msg.pages[current_page]    
    
                    await reaction.message.edit(embed=msg.curr_content)
                    await reaction.message.remove_reaction(reaction.emoji, user)
                            
                return
            async def set_embed_pageable(self, pages: t.List[discord.Embed],author: discord.Member, channel: discord.TextChannel, timeout: int = 60):
    
                if not isinstance(pages, t.List):
                    pages = [pages]
    
                pages = [e.copy() for e in pages]
    
                if not all(isinstance(p, discord.Embed) for p in pages):
                    raise Exception('All paginate embed pages need to be of type discord.Embed')
    
                footer = ''
                if not pages[0].footer.text == discord.Embed.Empty:
                    footer = pages[0].footer.text
    
                message = Message(pages,
                                  0,
                                  author.id if author else None,
                                  footer=footer)
                pages[0].set_footer(text=f'{footer}\nPage 1 of {len(pages)}')
                # send the first initial embed
                
    
    
                msg = await channel.send(embed=pages[0])
                await self.bot.messenger.publish(Events.on_set_deletable, msg=msg, author=msg.author)
    
                self.messages[msg.id] = message
                return_list= []
                return_list.append(msg)
                return_list.append(author)
                return_list.append(timeout)
                return_list.append(msg.id)
    
                
                return return_list
    
    
            async def send_scroll_reactions(self, msg: discord.Message, author: discord.Member, timeout: int):
                # add every emoji from the reaction list
                
                for reaction in ANSWER_KEY:
                    await msg.add_reaction(reaction)
                
                await self.bot.messenger.publish(Events.on_set_deletable, msg=msg, author=author)
                if timeout:
                    await asyncio.sleep(timeout)
                    try:
                        await msg.delete()
                    except:
                        pass
                    finally:
                        log.info('Message: {msg_id} timed out as pageable', msg_id=msg.id) 
                return None                    
               
def helper_fixer(formatthis):

         new_list = [f'#{formatthis.index(x)+1}.    {x}' for x in formatthis]
         return ['\n'.join(i) for i in chunk_list(new_list, CHUNK_SIZE)]  #Decided to implement chunking. Although useless now if the category lists expands alot it will be an easy fix.

def chunk_list(lst, n):
 for i in range(0, len(lst), n):   
    yield lst[i:i+n]       
CHUNK_SIZE = 24

ANSWER_KEY=['🇦',
            '🇧',
            '🇨',
            '🇩']


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

@dataclass
class Message:
    
        pages: t.Union[t.List[discord.Embed], t.List[str]]
        _curr_page_num: int
        author: int
        footer: str = None
        embed_name: str = None
        field_title: str = None
    
        @property
        def curr_page_num(self) -> int:
            return self._curr_page_num
    
        @curr_page_num.setter
        def curr_page_num(self, page_num: int):
            self._curr_page_num = page_num
    
        @property
        def curr_page(self) -> t.Union[discord.Embed, str]: #From Paginator cog
            return self.pages[self._curr_page_num]
    
        @property
        def curr_content(self) -> discord.Embed:
    
            page = self.curr_page
            if isinstance(page, discord.Embed):
    
                page.set_footer(text=f'{self.footer}\nPage {self.curr_page_num + 1} of {len(self.pages)}')
                return page
            elif not isinstance(page, str):
                raise Exception(f'Embed or string expected in the paginator service: {type(page)} found')
    
            embed = discord.Embed(title=self.embed_name, color=Colors.ClemsonOrange)
            embed.add_field(name=self.field_title, value=self.pages[self._curr_page_num])
            embed.set_footer(text=f'Page {self.curr_page_num + 1} of {len(self.pages)}')
    
            return embed
    
    
def setup(bot):
   bot.add_cog(TriviaCog(bot))
    