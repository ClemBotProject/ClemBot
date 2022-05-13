import json
import logging
import random
import aiohttp
import html
import asyncio
import typing as t
from dataclasses import dataclass
import discord
import discord.ext.commands as commands
from discord.ext.commands.errors import UserInputError
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
        "Use trivia to return a random assortment of 10 trivia questions. React with emojis to submit your answer choice")
    @commands.cooldown(1, 15, commands.BucketType.user)
    @ext.short_help(
        "Returns trivia questions")
    @ext.example("trivia")
    async def trivia(self, ctx):

        async with await self.session.get(DEFAULT_URL) as resp:
            parse_text = await resp.text()
            new_response = json.loads(parse_text)
            parsed_response = self.html_parser(new_response)

            #If you're curious as to why this doesn't check response code: It's because it will never NOT have questions for the default. If it does the website is down and it will error out anyway.

        best_list = await self.dict_publisher(parsed_response)  #Publishes the dictionary

        new_task = await self.asyncio_publisher(ctx, best_list[1])  #This returns key values for our list

          #Starts the event listener for the reaction BEFORE emojis are sent

        task1 = asyncio.create_task(self.send_scroll_reactions(ctx, new_task[0], new_task[1], new_task[2], new_task[4]))  #Sends the emojis for the reaction
        
        while not task1.done():  #Loops reading the user's reaction

            task_reaction = asyncio.create_task(self.on_reaction(ctx, new_task[3], new_task[2]))
            new_reaction = await task_reaction
            if new_reaction != None:
                page_int = await self.parse_reaction(ctx,new_task[0], new_reaction[0], new_reaction[1], best_list[0], page_int, new_task[4])
           
                 


    @trivia.command(aliases=['m'])
    @ext.long_help(
        "Specify arguments you want to return such as question number (max 35), category, difficulty, or question type. The arguments go: <Question Number> <category/substring/number> <Difficulty/Number> <question type/index>. With the only MANDATORY argument being question number. Use numbers for quicker specification of category by typing in the number beside the category in !help. Use 0 for unused categories! Say you want only bool question types (True/False) and default everything else: !trivia m 10 0 0 2 The only truly required argument is Question Number. You can use 0's for categories you don't want to specify")
    @ext.short_help(
            "trivia m allows specification of manual arguments. With as many or as few as you want using 0 for arguments you don't want")
    @commands.cooldown(1, 15, commands.BucketType.user)
    @ext.example(
        "trivia m <Question Number> <category/substring/number> <Difficulty/Number> <question type/index>")
    async def manual(self, ctx, *input: str):
        if len(input) < 1 or 4 < len(input):
            raise UserInputError("Invalid arguments! Specify between 1 to 4")

        function_parameters = []
        input_length = len(input)
        x = 0

        while x < input_length:
            append_this = await self.matching_function(x, *input)
            function_parameters.append(append_this)
            x += 1

        url = await self.url_builder(function_parameters, input_length)

        async with await self.session.get(url) as resp:
            response = json.loads(await resp.text())

        if response["response_code"] == 1:
            raise Exception(
                "There isn't enough questions in that category. Lower your question amount or select another! Or select a different question type!")

        parsed_response = self.html_parser(response)

        big_list = await self.dict_publisher(parsed_response)

        new_task = await self.asyncio_publisher(ctx, big_list[1])

        

        task1 = asyncio.create_task(self.send_scroll_reactions(ctx, new_task[0], new_task[1], new_task[2], new_task[4])) #Same deal as above

        
        while not task1.done():  #Loops reading the user's reaction

            task_reaction = asyncio.create_task(self.on_reaction(ctx, new_task[3], new_task[2]))
            new_reaction = await task_reaction
            if new_reaction != None:
                page_int = await self.parse_reaction(ctx,new_task[0], new_reaction[0], new_reaction[1], big_list[0], page_int, new_task[4])  #client.wait_for event listeners are fine. They get unloaded/disposed of at unload


    @trivia.command(aliases=['help'])
    @ext.long_help(
        "Lists the categories, difficulty, and type of questions. Useful for finding the index of categories!")
    @ext.short_help(
        "Use this to find the category you want!")
    @commands.cooldown(1, 30, commands.BucketType.user)
    @ext.example("trivia help")
    async def list_help(self, ctx):  #Overengineered this slightly. If the categories/difficulty/whatever else changes it will be a short fix

        final_page = []

        category_generator = helper_fixer(CATEGORYLIST)
       
        for x in category_generator:
            category_embed = discord.Embed(title="Category List:", color=Colors.ClemsonOrange)
            category_embed.add_field(name="Index:", value=x)

            final_page.append(category_embed)

        difficulty_generator = helper_fixer(DIFFICULTY)

      
        for y in difficulty_generator:
            difficulty_embed = discord.Embed(title="Difficulty List:", color=Colors.ClemsonOrange)
            difficulty_embed.add_field(name="Index:", value=y)

            final_page.append(difficulty_embed)
            

        question_generator = helper_fixer(QUESTIONTYPE)
        
        for z in question_generator:
            type_embed = discord.Embed(title="Question Type:", color=Colors.ClemsonOrange)
            type_embed.add_field(name="Index:", value=z)

            final_page.append(type_embed)
          

        await self.bot.messenger.publish(Events.on_set_pageable_embed,
                                         pages=final_page,
                                         author=ctx.author,
                                         channel=ctx.channel,
                                         timeout=60,)


    async def url_builder(self, function_list, input_length):

        max_index = input_length - 1
        url = URL_BUILDER + str(function_list[0])
        x = 1


        while x <= max_index:
            if function_list[x]:
                match x:
                    case 1:
                       url= (f"{url}&category={str(function_list[1])}")
                    case 2:
                        url = (f"{url}&difficulty={function_list[2]}")
                    case 3:
                        url = (f"{url}&type={function_list[max_index]}")
            x += 1

        return url

    async def matching_function(self, case, *input: str):

        match case:  #Revolves around beautiful O(1) based indexing
            case 0:
                if input[0].isnumeric():
                    question_number = int(input[0])

                    if 0 < question_number <= 50:
                        return question_number
                    else:
                        raise UserInputError(
                            "Question Number entered is out of range!")
                else:
                    raise UserInputError(
                        "Question Number has to be a number within the range of 1 to 50")
            case 1:
                if input[1].isnumeric():
                    trivia_number = int(input[1])
                    if 0 < trivia_number <= 24:
                        return trivia_number + 8
                    elif trivia_number == 0:
                        return None
                    else:
                        raise UserInputError(
                            "Category Number out of bounds(Number has to be 1-24) or enter the category you want! Type ?trivia help to see the category list")
                else:
                    trivia_category = input[1].lower()

                    for x in CATEGORYLIST_LOWER:
                        if x.find(trivia_category) != -1:
                            return_this = CATEGORYLIST_LOWER.index(x) + 9
                            return return_this
                    else:
                        raise UserInputError("Category not found!")
            case 2:
                if input[2].isnumeric():
                    evaluate_int = int(input[2])
                    if 0 < evaluate_int <= 3:
                        return_string = DIFFICULTY_LOWER[evaluate_int - 1]
                        return return_string
                    elif evaluate_int == 0:
                        return None
                    else:
                        raise UserInputError(
                            "Difficulty Number out of bounds(Number has to be 1-3) or enter Easy-Hard! Type ?trivia help to see the difficulty list.")
                else:
                    difficulty = input[2].lower()
                    for x in DIFFICULTY_LOWER:

                        if (x.find(difficulty) != -1):  #Searches the substring. If this ever comes up, its not a bug you can type in a and not find your category GIGO. It is better than exact case parsing.
                            return x
                    else:
                        raise UserInputError("Difficulty not found")
            case 3:
                if input[3].isnumeric():
                    evaluate_int = int(input[3])
                    if 0 < evaluate_int < 3:
                        final_return = QUESTIONTYPE[evaluate_int - 1]
                        return final_return
                    elif evaluate_int == 0:
                        return None
                    else:
                        raise UserInputError(
                            "Question type number out of bounds(1 or 2) 1: Multiple Choice 2: Boolean. Type ?trivia help to see our question types.")
                else:
                    question_type = input[3].lower()
                    for x in QUESTIONTYPE:
                        if (x.find(question_type) != -1):
                            return x
                    else:
                        raise UserInputError(
                            "Couldn't find the question type you are looking for!.")

    def html_parser(self, new_response):

        dictionary_list = []  #pain

        for x in new_response['results']:
            new_dictionary = x
            new_list_values = x.values()
            proper_values = []

            for b in new_list_values:
                if isinstance(b, list):
                    new_list = []
                    for y in b:
                        if not y.isnumeric():
                            new_list.append(html.unescape(y))  #This HTML response is in a weird format where you have to navigate a list that contains dictionaries with that dictionary containing a SINGLE list
                        else:
                            new_list.append(y)
                    proper_values.append(new_list)
                elif not b.isnumeric():
                    proper_values.append(html.unescape(b))  # good luck maintaining this
                else:
                    proper_values.append(b)

            proper_values_size = len(proper_values)
            biggest_loop = 0

            for key, value in new_dictionary.items():  #.items is special because it contains an active view
                new_dictionary[key] = proper_values[biggest_loop]
                if biggest_loop < proper_values_size:
                    biggest_loop += 1
                else:
                    break

            dictionary_list.append(new_dictionary)

        dictionary_size = len(new_response['results'])
        best_loopint = 0

        while best_loopint < dictionary_size:
            new_response['results'][best_loopint] = dictionary_list[best_loopint]  #Sets the real dictionary to our parsed results
            best_loopint += 1

        return new_response

    async def dict_publisher(self, dictionary):

        x = 0
        cog_embeds = []
        list_index = []

        for create_lists in dictionary['results']:

            answers_list = create_lists['incorrect_answers']
            answers_list.append(create_lists['correct_answer'])
            right_answer = create_lists['correct_answer']

            random.shuffle(answers_list)
            list_index.append(answers_list.index(right_answer))
      
            x += 1
            embed = discord.Embed(title=f"Question # {str(x)}:",color=Colors.ClemsonOrange)

            embed.add_field(name="Question:", value=create_lists['question'])
            embed.add_field(name="Category:", value=create_lists['category'])

            a = 65
            for iterative in answers_list:
                embed.add_field(name=f"Answer Choice  {chr(a)}:", value=iterative, inline=False)
                a = a + 1

            cog_embeds.append(embed)

        mega_list = []
        mega_list.append(list_index)
        mega_list.append(cog_embeds)  #Returns pages needed for pagination and a INDEX based value for what the answer is. e.g 0 = A 1 = B.

        return mega_list

    async def asyncio_publisher(self, ctx, cog_embeds):

        embed_list = await self.set_embed_pageable(cog_embeds, ctx.author, ctx.channel, len(cog_embeds) * 3)
        return embed_list

    async def on_reaction(self, ctx, message, timeout: int):
       
        author = ctx.author
        def check(reaction, user):
            return user == author and reaction.message.id == message
        try:
            reaction, user = await self.bot.wait_for("reaction_add",timeout=timeout, check=check)
        except:
            return None


        return_list = []
        return_list.append(reaction)  #Returning this
        return_list.append(user)

        return return_list

    async def parse_reaction(self,ctx, message, reaction, user, right_answer, page_int, total_questions):

        msg = self.messages[reaction.message.id]  #If you actually refrence msg.curr_page_num every time it performs a lookup -> to the class rather than a constant
        CURRENT_PAGE = 0 #Current page will ALWAYS be 0 because it deletes each question as it goes along. page_int keeps track of the page
        match reaction.emoji:
            case '🇦':
                if right_answer[page_int] == 0:  # parsing reactions with match case because it is slightly quicker
                    msg.score_setter+=1
                    
            case '🇧':
                if right_answer[page_int] == 1:  #TODO: Implement scoring/ Database system!
                    msg.score_setter+=1
                    

            case '🇨':            
                if right_answer[page_int] == 2:
                    msg.score_setter+=1
                    

            case '🇩':
                if right_answer[page_int] == 3:  #It's not a bug that A,B,C,D also show up for boolean questions. Implementing the required logic to remove/add emojis based on the CURRENT pages fields/titles would make this already shaky embed so much slower. If the answer choices are A or B and you pick C its still wrong.
                   msg.score_setter+=1

        
        if len(msg.pages) <= 1:
            await self.scoreboard_embed(ctx, msg.score, total_questions)
            await message.delete()  #Deletes embed if the page queue has runout
            return
        else:
            del msg.pages[CURRENT_PAGE]
            page_int+=1
            await reaction.message.edit(embed=msg.curr_content)
            await reaction.message.remove_reaction(reaction.emoji, user)

        return page_int

    async def set_embed_pageable(self, pages: t.List[discord.Embed], author: discord.Member, channel: discord.TextChannel, timeout: int):

        if not isinstance(pages, t.List):
            pages = [pages]

        pages = [e.copy() for e in pages]

        if not all(isinstance(p, discord.Embed) for p in pages):
            raise Exception('All paginate embed pages need to be of type discord.Embed')
        pages_length = len(pages)
        footer = ''
        if not pages[0].footer.text == discord.Embed.Empty:
            footer = pages[0].footer.text

        message = Message(pages,
                          0,
                          author.id if author else None,
                          footer=footer)
        pages[0].set_footer(text=f'{footer}\nPage 1 of {len(pages)} Score: 0')
        # send the first initial embed

        msg = await channel.send(embed=pages[0])
        await self.bot.messenger.publish(Events.on_set_deletable, msg=msg, author=msg.author)

        self.messages[msg.id] = message

        return_list = []
        return_list.append(msg)
        return_list.append(author)
        return_list.append(timeout)
        return_list.append(msg.id)
        return_list.append(pages_length)

        return return_list
    async def scoreboard_embed(self, ctx, score, total_questions):
        current_author = ctx.author
        percent_questions = (score/total_questions)*100
        score_embed = discord.Embed(title=(f"{current_author}'s score for this round is:  {score} out of {total_questions} this is {percent_questions}% correct"), color=Colors.ClemsonOrange)
        await ctx.send(embed=score_embed) 


    async def send_scroll_reactions(self,ctx, msg: discord.Message, author: discord.Member, timeout: int, total_questions):
        # add every emoji from the reaction list
       
        for reaction in ANSWER_KEY:
            await msg.add_reaction(reaction)  #Removed arrows because I made the decision it made the embed look too clunky, took too long to add, and added unneeded complexity

        await self.bot.messenger.publish(Events.on_set_deletable, msg=msg, author=author)
        
        if timeout:
            await asyncio.sleep(timeout)
            try:
                channel = ctx.channel
                cog_message = self.messages[msg.id]
                message_checker = await channel.fetch_message(msg.id)

                if message_checker != None:
                    await self.scoreboard_embed(ctx, cog_message.score, total_questions)
                    await msg.delete()  #Prevents storing useless trivia questions. I might implement a scorecard embed so people have proof that they can win virtual trivia? It would publish the embed then delete the questions
            except:
                pass
            finally:
                log.info('Message: {msg_id} timed out as pageable', msg_id=msg.id)
        return 1
    

def helper_fixer(format_this):
    new_list = [f'#{format_this.index(x) + 1}.    {x}' for x in format_this]
    return ['\n'.join(i) for i in chunk_list(new_list, CHUNK_SIZE)]  #Decided to implement chunking. Although useless now if the category lists expands alot it will be an easy fix.


def chunk_list(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


CHUNK_SIZE = 24

ANSWER_KEY = ['🇦',
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

CATEGORYLIST = ["General-Knowledge",  #Including this out of consistency to avoid making the offset 10 for no reason. This will be the default value.
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
    score: int = 0
    

    @property
    def curr_page_num(self) -> int:
        return self._curr_page_num

    @property
    def score_setter(self) -> int:
        return self.score
    @property
    def curr_score(self) -> int:
        return self.score

    @curr_page_num.setter
    def curr_page_num(self, page_num: int):
        self._curr_page_num = page_num

    @score_setter.setter
    def score_setter(self, score: int):
        self.score = score
    @property
    def curr_page(self) -> t.Union[discord.Embed, str]:  #From Paginator cog
        return self.pages[self._curr_page_num]

    @property
    def curr_content(self) -> discord.Embed:

        page = self.curr_page
        score = self.curr_score
        if isinstance(page, discord.Embed):

            page.set_footer(text=f"{self.footer}\nPage {self.curr_page_num + 1} of {len(self.pages)} Score: {score}")
            return page
        elif not isinstance(page, str):
            raise Exception(f"Embed or string expected in the paginator service: {type(page)} found")

        embed = discord.Embed(title=self.embed_name, color=Colors.ClemsonOrange)
        embed.add_field(name=self.field_title, value=self.pages[self._curr_page_num])
        embed.set_footer(text=f"Page {self.curr_page_num + 1} of {len(self.pages)}")

        return embed


def setup(bot):
    bot.add_cog(TriviaCog(bot))
