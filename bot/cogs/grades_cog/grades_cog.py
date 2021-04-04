import json
import os
import gzip
import logging
import collections
import itertools

import discord
import pandas as pd
import discord.ext.commands as commands
from bot.messaging.events import Events
import typing as t

from bot.consts import Colors
import bot.extensions as ext
from spellchecker import SpellChecker # Here we will add a utility for correcting user input

log = logging.getLogger(__name__)

MIN_YEAR = 2014
TAG_CHUNK_SIZE = 12*3
CSV_FILES = [
    '2014_Fall.csv',
    '2015_Fall.csv',
    '2015_Fall.csv',
    '2016_Fall.csv',
    '2017_Fall.csv',
    '2018_Fall.csv',
    '2019_Fall.csv',
    '2020_Fall.csv',
    '2014_Spring.csv',
    '2015_Spring.csv',
    '2015_Spring.csv',
    '2016_Spring.csv',
    '2017_Spring.csv',
    '2018_Spring.csv',
    '2019_Spring.csv',
]

ASSET_LOCATION = 'bot/cogs/grades_cog/assets/'

class GradesCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.load_data()

    def load_data(self):
        self.grades_df = pd.DataFrame()
        for file in CSV_FILES:
            self.grades_df = self.grades_df.append(pd.read_csv(f'{ASSET_LOCATION}{file}'))

        self.grades_df.info()

        self.all_profs = self.get_profs()
        self.all_courses = self.get_courses()

    @ext.group(invoke_without_command= True, case_insensitive=True)
    @ext.long_help(
        """
        Attempts to give more information about courses at Clemson University.

        DISCLAIMER:
        Not every professor listed will be at Clemson, this is a tool built for better information but not complete information.
        In addition, this system works on the Grade Distribution Releases located at https://www.clemson.edu/institutional-effectiveness/oir/data-reports/
        In Addition, Clemson provides incomplete and mangled professor data so there will be multiple different versions of the same professor. This is just a byproduct of how the data is distributed from the university
        """
    )
    @ext.short_help('Attempts to give more information about courses at Clemson University')
    @ext.example(('grades cpsc-1010', 'grades cpsc-1010 2017'))
    async def grades(self, ctx, course: str, year: int=MIN_YEAR):
        course = course.upper()

        if not self.grades_df.CourseId.str.contains(course).any():
            embed = discord.Embed(title="Grades", color=Colors.Error)
            result = 'Are you sure you used the proper notation (ex: cpsc-2120)?'
            embed.add_field(name="ERROR: Course doesn't exist", value=result, inline=False)
            embed.add_field(name=f'Help:', value= f'Run `{await self.bot.current_prefix(ctx)}grades list` to find what courses are available', inline=False)
            return await ctx.send(embed=embed)

        df = self.grades_df[(self.grades_df.CourseId == course) & (self.grades_df.Year >= year)]
        log.info(df)
        A = f'{int(df.A.mean().round(2) * 100)}%'
        B = f'{int(df.B.mean().round(2) * 100)}%'
        C = f'{int(df.C.mean().round(2) * 100)}%'
        D = f'{int(df.D.mean().round(2) * 100)}%'
        F = f'{int(df.F.mean().round(2) * 100)}%'
        W = f'{int(df.W.mean().round(2) * 100)}%'

        embeds = []

        embed = discord.Embed(title=f'Grades for {course} since {year}', color=Colors.ClemsonOrange)
        embed.set_footer(text=self.get_full_name(ctx.author), icon_url=ctx.author.avatar_url)
        embed.add_field(name='Overall Distribution', value=f'```A: {A}\nB: {B}\nC: {C}\nD: {D}\nF: {F}\nW: {W}```')
        embed.add_field(name='Total Number of Classes Analyzed', value=len(df), inline=False)
        embed.add_field(name='Total Number of Professors Found', value=len(df.groupby(['Instructor'])), inline=False)
        embed.add_field(name='Explanation',value=f'Run `{await self.bot.current_prefix(ctx)}help grades` for more information on this command')
        embeds.append(embed)

        for i, row in df.groupby(['Instructor']).mean().iterrows():
            embed = discord.Embed(title=f'Grades for {course} since {year}', color=Colors.ClemsonOrange) 
            embed.set_footer(text=self.get_full_name(ctx.author), icon_url=ctx.author.avatar_url)
            A = f'{int(row.A.round(2) * 100)}%'
            B = f'{int(row.B.round(2) * 100)}%'
            C = f'{int(row.C.round(2) * 100)}%'
            D = f'{int(row.D.round(2) * 100)}%'
            F = f'{int(row.F.round(2) * 100)}%'
            W = f'{int(row.W.round(2) * 100)}%'

            val = f'```A: {A}%\nB: {B}\nC: {C}\nD: {D}\nF: {F}\nW: {W}```'
            embed.add_field(name=f"{row.name}'s distribution", value=val)
            embed.add_field(name='Total Number of Classes Analyzed', value=len(df), inline=False)
            embed.add_field(name='Total Number of Professors Found', value=len(df.groupby(['Instructor'])), inline=False)
            embed.add_field(name='Explanation',value=f'Run `{await self.bot.current_prefix(ctx)}help grades` for more information on this command')
            embeds.append(embed)

        await self.bot.messenger.publish(Events.on_set_pageable_embed, 
            pages=embeds, 
            author=ctx.author, 
            channel=ctx.channel,
            timeout=360)

    @ext.group(invoke_without_command= True, case_insensitive=True)
    @ext.long_help(
        """
        Attempts to give more information about professor's grade distribution at Clemson.

        DISCLAIMER:
        Not every professor listed will be at Clemson, this is a tool built for better information but not complete information.
        In addition, this system works on the Grade Distribution Releases located at https://www.clemson.edu/institutional-effectiveness/oir/data-reports/
        In Addition, Clemson provides incomplete and mangled professor data so there will be multiple different versions of the same professor. This is just a byproduct of how the data is distributed from the university
        """
    )
    @ext.short_help('Provides info about a given professor')
    @ext.example(('prof brian dean', 'prof brian dean'))
    async def prof(self, ctx, *, prof: str):
        prof = prof.lower()
        normalized_name = prof.title()

        if not self.grades_df.Instructor.str.contains(prof).any():
            embed = discord.Embed(title="Professors", color=Colors.Error)
            result = f'"{prof}" is not a known Professor\n'
            embed.add_field(name="ERROR: Professor doesn't exist", value=result, inline=False)
            embed.add_field(name=f'Help:', value= f'Run `{await self.bot.current_prefix(ctx)}prof list` to find what proffesors are available', inline=False)
            return await ctx.send(embed=embed)#chunk the list of tags into groups of TAG_CHUNK_SIZE for each page

        #check for if there is a 0% A rate, that means it was a pass fail class and we dont handle those
        df = self.grades_df[(self.grades_df.Instructor == prof) & (self.grades_df.A > 0)]
        A = f'{int(df.A.mean().round(2) * 100)}%'
        B = f'{int(df.B.mean().round(2) * 100)}%'
        C = f'{int(df.C.mean().round(2) * 100)}%'
        D = f'{int(df.D.mean().round(2) * 100)}%'
        F = f'{int(df.F.mean().round(2) * 100)}%'
        W = f'{int(df.W.mean().round(2) * 100)}%'

        embeds = []

        embed = discord.Embed(title=f'Overall Grade Distribution for {normalized_name} across all classes taught', color=Colors.ClemsonOrange)
        embed.set_footer(text=self.get_full_name(ctx.author), icon_url=ctx.author.avatar_url)
        embed.add_field(name='Overall Distribution', value=f'```A: {A}\nB: {B}\nC: {C}\nD: {D}\nF: {F}\nW: {W}```')
        embed.add_field(name='Total Number of Classes Analyzed', value=len(df.groupby(['CourseId'])), inline=False)
        embed.add_field(name='Explanation',value=f'Run `{await self.bot.current_prefix(ctx)}help grades` for more information on this command')
        embeds.append(embed)

        for i, row in df.groupby(['CourseId']).mean().iterrows():
            embed = discord.Embed(title=f'Grade Distribution for {normalized_name}', color=Colors.ClemsonOrange)
            embed.set_footer(text=self.get_full_name(ctx.author), icon_url=ctx.author.avatar_url)
            A = f'{int(row.A.round(2) * 100)}%'
            B = f'{int(row.B.round(2) * 100)}%'
            C = f'{int(row.C.round(2) * 100)}%'
            D = f'{int(row.D.round(2) * 100)}%'
            F = f'{int(row.F.round(2) * 100)}%'
            W = f'{int(row.W.round(2) * 100)}%'

            val = f'```A: {A}%\nB: {B}\nC: {C}\nD: {D}\nF: {F}\nW: {W}```'
            embed.add_field(name=f"{row.name}'s distribution", value=val)
            embed.add_field(name='Total Number of Classes Analyzed', value=len(df), inline=False)
            embed.add_field(name='Explanation',value=f'Run `{await self.bot.current_prefix(ctx)}help grades` for more information on this command')
            embeds.append(embed)

        await self.bot.messenger.publish(Events.on_set_pageable_embed, 
            pages=embeds, 
            author=ctx.author, 
            channel=ctx.channel,
            timeout=360)

    def get_courses(self):
        grades = self.grades_df.groupby(['CourseId']).mean().iterrows()

        pages = []

        #begin generating paginated columns
        for chunk in self.chunk_list([prof.name for i, prof in grades], 51):

            #we need to create the columns on the page so chunk the list again
            content = ''
            for col in self.chunk_list(chunk, 3):
                #the columns wont have the perfect number of elements every time, we need to append spaces if
                #the list entries is less then the number of columns
                while len(col) <3:
                    col.append(' ')

                #Cocatenate the formatted column string to the page content string
                content += "{: <12} {: <12} {: <12}\n".format(*col)

            #Apped the content string to the list of pages to send to the paginator
            #Marked as a code block to ensure a monospaced font and even columns
            pages.append(f'```{content}```')

        return pages

    @grades.command(aliases=['list'])
    async def list_grades(self, ctx):
        await self.bot.messenger.publish(Events.on_set_pageable_text,
                embed_name='All Known Professors', 
                field_title='Listing:',
                pages=self.all_courses, 
                author=ctx.author, 
                channel=ctx.channel)

    def get_profs(self):
        profs = self.grades_df.groupby(['Instructor']).mean().iterrows()

        pages = []

        #begin generating paginated columns
        #chunk the list of tags into groups of TAG_CHUNK_SIZE for each page
        for chunk in self.chunk_list([prof.name for i, prof in profs], TAG_CHUNK_SIZE):

            #we need to create the columns on the page so chunk the list again
            content = ''
            for col in self.chunk_list(chunk, 2):
                #the columns wont have the perfect number of elements every time, we need to append spaces if
                #the list entries is less then the number of columns
                while len(col) <3:
                    col.append(' ')

                #Cocatenate the formatted column string to the page content string
                content += "{: <24}  {: <24}\n".format(*col)

            #Apped the content string to the list of pages to send to the paginator
            #Marked as a code block to ensure a monospaced font and even columns
            pages.append(f'```{content}```')

        return pages

    @prof.command(aliases=['list'])
    async def list_prof(self, ctx):
        await self.bot.messenger.publish(Events.on_set_pageable_text,
                embed_name='All Known Professors', 
                field_title='Listing:',
                pages=self.all_profs, 
                author=ctx.author, 
                channel=ctx.channel)

    def get_full_name(self, author) -> str: 
        return f'{author.name}#{author.discriminator}' 

    def chunk_list(self, lst, n):
        """Yield successive n-sized chunks from lst."""
        for i in range(0, len(lst), n):
            yield lst[i:i + n]

def setup(bot):
    bot.add_cog(GradesCog(bot))
