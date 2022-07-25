import logging
import random
import aiohttp
import html
import asyncio
import typing as t
from dataclasses import dataclass
from bot.utils.helpers import chunk_sequence
import discord
import discord.ext.commands as commands
from discord.ext.commands.errors import UserInputError
from bot.utils.converters import trivia_cog_converter
import bot.extensions as ext
from bot.consts import Colors
from bot.messaging.events import Events
import seqlog

log: seqlog.StructuredLogger = logging.getLogger(__name__)  # type: ignore


class TriviaCog(commands.Cog):

    def cog_unload(self):
        self.session.close()

    def __init__(self, bot):
        self.messages = {}
        self.bot = bot
        self.session = aiohttp.ClientSession(headers={"Connection": "keep-alive"})

    @ext.group(case_insensitive=True, invoke_without_command=True)
    @ext.long_help(
        "Use trivia to return a random assortment of 10 trivia questions. React with emojis to submit your answer choice")
    @commands.cooldown(1, 15, commands.BucketType.user)
    @ext.short_help(
        "Returns trivia questions")
    @ext.example("trivia")
    async def trivia(self, ctx):

        async with self.session.get(DEFAULT_URL) as resp:
            parsed_response = self.html_parser(await resp.json())

            # If you're curious as to why this doesn't check response code: It's because it will never NOT have questions for the default. If it does the website is down and it will error out anyway.

        best_list = await self.dict_publisher(parsed_response)  #Publishes the dictionary

        new_task = await self.asyncio_publisher(ctx, best_list[1])  #This returns key values for our list

        # Starts the event listener for the reaction BEFORE emojis are sent

        task_1 = asyncio.create_task(self.send_scroll_reactions(ctx, new_task[0], new_task[1], new_task[2], new_task[4]))  # Sends the emojis for the reaction
        page_int = 0

        while not task_1.done():  # Loops reading the user's reaction
            new_reaction = await self.on_reaction(ctx, new_task[3], new_task[2])

            if new_reaction is not None:
                page_int = await self.parse_reaction(ctx,new_task[0], new_reaction[0], new_reaction[1], best_list[0], page_int, new_task[4])
       
    @trivia.command(aliases=['m'])
    @ext.long_help(
        "Specify arguments you want to return such as question number (max 35), category, difficulty, or question type. The arguments go: <Question Number> <category/substring/number> <Difficulty/Number> <question type/index>. With the only MANDATORY argument being question number. Use numbers for quicker specification of category by typing in the number beside the category in !help. Use 0 for unused categories! Say you want only bool question types (True/False) and default everything else: !trivia m 10 0 0 2 The only truly required argument is Question Number. You can use 0's for categories you don't want to specify")
    @ext.short_help(
            "trivia m allows specification of manual arguments. With as many or as few as you want using 0 for arguments you don't want")
    @commands.cooldown(1, 15, commands.BucketType.user)
    @ext.example(
        "trivia m <Question Number> <category/substring/number> <Difficulty/Number> <question type/index>")
    async def manual(self, ctx, *input_list: str):
        input_length = len(input_list)
        if input_length < 1 or 4 < input_length:
            raise UserInputError("Invalid arguments! Specify between 1 to 4")

        url = trivia_cog_converter(input_length, input_list)
        
        async with self.session.get(url) as resp:
            response = await resp.json()

        if response["response_code"] == 1:
            raise Exception(
                "There isn't enough questions in that category. Lower your question amount or select another! Or select a different question type!")

        parsed_response = self.html_parser(response)

        big_list = await self.dict_publisher(parsed_response)

        new_task = await self.asyncio_publisher(ctx, big_list[1])
        
        task1 = asyncio.create_task(self.send_scroll_reactions(ctx, new_task[0], new_task[1], new_task[2], new_task[4])) #Same deal as above
        page_int = 0

        while not task1.done():  # Loops reading the user's reaction
            new_reaction = await self.on_reaction(ctx, new_task[3], new_task[2])
            if new_reaction is not None:
                page_int = await self.parse_reaction(ctx,new_task[0], new_reaction[0], new_reaction[1], big_list[0], page_int, new_task[4])  #client.wait_for event listeners are fine. They get unloaded/disposed of at unload


    @trivia.command(aliases=["help"])
    @ext.long_help(
        "Lists the categories, difficulty, and type of questions. Useful for finding the index of categories!")
    @ext.short_help(
        "Use this to find the category you want!")
    @commands.cooldown(1, 30, commands.BucketType.user)
    @ext.example("trivia help")
    async def list_help(self, ctx):  #Overengineered this slightly. If the categories/difficulty/whatever else changes it will be a short fix

        final_page = []

        category_generator = helper_fixer(CATEGORY_LIST)
       
        for x in category_generator:
            category_embed = discord.Embed(title="Category List:", color=Colors.ClemsonOrange)
            category_embed.add_field(name="Index:", value=x)

            final_page.append(category_embed)

        difficulty_generator = helper_fixer(DIFFICULTY)

        for y in difficulty_generator:
            difficulty_embed = discord.Embed(title="Difficulty List:", color=Colors.ClemsonOrange)
            difficulty_embed.add_field(name="Index:", value=y)

            final_page.append(difficulty_embed)

        question_generator = helper_fixer(QUESTION_TYPE)
        
        for z in question_generator:
            type_embed = discord.Embed(title="Question Type:", color=Colors.ClemsonOrange)
            type_embed.add_field(name="Index:", value=z)

            final_page.append(type_embed)
          
        await self.bot.messenger.publish(Events.on_set_pageable_embed,
                                         pages=final_page,
                                         author=ctx.author,
                                         channel=ctx.channel,
                                         timeout=60,)

    def html_parser(self, new_response):
        dictionary_list = []  # pain

        for x in new_response["results"]:
            new_dictionary = x
            new_list_values = x.values()
            proper_values = []

            for b in new_list_values:
                if isinstance(b, list):
                    new_list = []
                    for y in b:
                        if not y.isnumeric():
                            new_list.append(html.unescape(y))  # This HTML response is in a weird format where you have to navigate a list that contains dictionaries with that dictionary containing a SINGLE list
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

        dictionary_size = len(new_response["results"])
       
        for best_loopint in range (0,dictionary_size):
            new_response["results"][best_loopint] = dictionary_list[best_loopint]  # Sets the real dictionary to our parsed results

        return new_response

    async def dict_publisher(self, dictionary):
        cog_embeds = []
        list_index = []

        for x, create_lists in enumerate(dictionary["results"], start=1):
            answers_list = create_lists["incorrect_answers"]
            answers_list.append(create_lists["correct_answer"])
            right_answer = create_lists["correct_answer"]

            random.shuffle(answers_list)
            list_index.append(answers_list.index(right_answer))
            
            embed = discord.Embed(title=f"Question # {str(x)}:",color=Colors.ClemsonOrange)

            embed.add_field(name="Question:", value=create_lists["question"])
            embed.add_field(name="Category:", value=create_lists["category"])

            a = 65
            for iterative in answers_list:
                embed.add_field(name=f"Answer Choice  {chr(a)}:", value=iterative, inline=False)
                a = a + 1

            cog_embeds.append(embed)

        mega_list = []
        mega_list.append(list_index)
        mega_list.append(cog_embeds)  # Returns pages needed for pagination and a INDEX based value for what the answer is. e.g 0 = A 1 = B.

        return mega_list

    async def asyncio_publisher(self, ctx, cog_embeds):
        embed_list = await self.set_embed_pageable(cog_embeds, ctx.author, ctx.channel, len(cog_embeds) * 10)
        return embed_list

    async def on_reaction(self, ctx, message, timeout: int):
        author = ctx.author

        def check(reaction, user):
            return user == author and reaction.message.id == message

        try:
            reaction, user = await self.bot.wait_for("reaction_add", timeout=timeout, check=check)
        except:
            return None

        return_list = []
        return_list.append(reaction)  #Returning this
        return_list.append(user)

        return return_list

    async def parse_reaction(self,ctx, message, reaction, user, right_answer, page_int, total_questions):
        msg = self.messages[reaction.message.id]  # If you actually refrence msg.curr_page_num every time it performs a lookup -> to the class rather than a constant
        
        # TODO: Implement scoring/ Database system!
        # It's not a bug that A,B,C,D also show up for boolean questions. Implementing the required logic to remove/add emojis based on the CURRENT pages fields/titles would make this already shaky embed so much slower. If the answer choices are A or B and you pick C its still wrong.
        if right_answer[page_int] == ANSWER_KEY.index(reaction.emoji):
            msg.score_setter += 1

        if len(msg.pages) <= 1:
            await self.scoreboard_embed(ctx, msg.score, total_questions)
            await message.delete()  # Deletes embed if the page queue has runout
            return
        else:
            del msg.pages[0]
            page_int+=1
            await reaction.message.edit(embed=msg.curr_content)
            await reaction.message.remove_reaction(reaction.emoji, user)

        return page_int

    async def set_embed_pageable(self, pages: list[discord.Embed], author: discord.Member, channel: discord.TextChannel, timeout: int):
        if not isinstance(pages, t.List):
            pages = [pages]

        pages = [e.copy() for e in pages]

        if not all(isinstance(p, discord.Embed) for p in pages):
            raise Exception("All paginate embed pages need to be of type discord.Embed")

        pages_length = len(pages)
        footer = ''
        if not pages[0].footer.text == discord.Embed.Empty:
            footer = pages[0].footer.text

        message = Message(pages,
                          0,
                          author.id if author else None,
                          footer=footer)
        pages[0].set_footer(text=f"{footer}\nPage 1 of {len(pages)} Score: 0")
        
        # send the first initial embed
        msg = await channel.send(embed=pages[0])
        await self.bot.messenger.publish(Events.on_set_deletable, msg=msg, author=msg.author)

        self.messages[msg.id] = message

        return [msg, author, timeout, msg.id, pages_length]

    async def scoreboard_embed(self, ctx, score, total_questions):
        current_author = ctx.author
        percent_questions = round((score/total_questions)*100,2)
        score_embed = discord.Embed(title=(f"{current_author}'s score for this round is:  {score} out of {total_questions} this is {percent_questions}% correct"), color=Colors.ClemsonOrange)
        await ctx.send(embed=score_embed) 

    async def send_scroll_reactions(self,ctx, msg: discord.Message, author: discord.Member, timeout: int, total_questions):
        # add every emoji from the reaction list
       
        for reaction in ANSWER_KEY:
            await msg.add_reaction(reaction)  # Removed arrows because I made the decision it made the embed look too clunky, took too long to add, and added unneeded complexity

        await self.bot.messenger.publish(Events.on_set_deletable, msg=msg, author=author)
        
        if timeout:
            await asyncio.sleep(timeout)
            try:
                channel = ctx.channel
                cog_message = self.messages[msg.id]
                message_checker = await channel.fetch_message(msg.id)
                await self.scoreboard_embed(ctx, cog_message.score, total_questions)
                if message_checker is not None:
                    await msg.delete()  # Prevents storing useless trivia questions. I might implement a scorecard embed so people have proof that they can win virtual trivia? It would publish the embed then delete the questions
            except:
                pass
            finally:
                log.info("Message: {msg_id} timed out as pageable", msg_id=msg.id)    

def helper_fixer(format_this):
    new_list = [f"#{format_this.index(x) + 1}.    {x}" for x in format_this]
    return ['\n'.join(i) for i in chunk_sequence(new_list, CHUNK_SIZE)]  # Decided to implement chunking. Although useless now if the category lists expands alot it will be an easy fix.


CHUNK_SIZE = 24

ANSWER_KEY = ['🇦',
              '🇧',
              '🇨',
              '🇩']

URL_BUILDER = "https://opentdb.com/api.php?amount="

DEFAULT_URL = "https://opentdb.com/api.php?amount=10"

DIFFICULTY = ["Easy",
              "Medium",
              "Hard"]

DIFFICULTY_LOWER = [k.lower() for k in DIFFICULTY]

QUESTION_TYPE = [
    "multiple",
    "boolean"
]

CATEGORY_LIST = ["General-Knowledge",  # Including this out of consistency to avoid making the offset 10 for no reason. This will be the default value.
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

CATEGORY_LIST_LOWER = [k.lower() for k in CATEGORY_LIST]


@dataclass
class Message:
    pages: t.Union[list[discord.Embed], list[str]]
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
