import os
import logging

import discord
import pandas as pd
import discord.ext.commands as commands
from bot.messaging.events import Events

from bot.consts import Colors
import bot.extensions as ext

log = logging.getLogger(__name__)

MIN_YEAR = 2014
TAG_CHUNK_SIZE = 12 * 3

ASSET_LOCATION = 'bot/cogs/grades_cog/assets/'


class GradesCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.load_data()

    def load_data(self):
        self.grades_df = pd.DataFrame()
        for file in os.listdir(ASSET_LOCATION):
            self.grades_df = self.grades_df.append(pd.read_csv(f'{ASSET_LOCATION}{file}'))

        self.grades_df.info()

        self.all_profs = self.get_profs()
        self.all_courses = self.get_courses()

    @ext.group(invoke_without_command=True, case_insensitive=True)
    @ext.long_help(
        """
        Attempts to give more information about courses at Clemson University.
        
        General usage:
        `grades [course] (year) (honors|non-honors|all)`
        
        Where `course` is required, but the `year` and `honors` arguments are optional.
        
        Default `year`: `2014`.
        Default `honors` argument: `all` (this averages grades for every section in a course, whether honors or non-honors).

        DISCLAIMER:
        Not every professor listed will be at Clemson, this is a tool built for better information but not complete information.
        In addition, this system works on the Grade Distribution Releases located at https://www.clemson.edu/institutional-effectiveness/oir/data-reports/
        In Addition, Clemson provides incomplete and mangled professor data so there will be multiple different versions of the same professor. This is just a byproduct of how the data is distributed from the university
        """
    )
    @ext.short_help('Attempts to give more information about courses at Clemson University')
    @ext.example(
        ('grades math-2060', 'grades math-2060 2017', 'grades math-2060 honors', 'grades math-2060 2017 honors'))
    async def grades(self, ctx, course: str, *args):
        course = course.upper()

        # Defaults
        honors = "all"
        year = MIN_YEAR

        error_title = False
        error_message = False

        # We have flexibility of the order and exact phrasing of arguments
        for arg in args:
            if arg in ("honors", "hon"):
                honors = "honors"
            elif arg in ("non-honors", "non-hon", "regular", "normal"):
                honors = "non-honors"
            elif arg == "all":
                honors = "all"
            elif arg.isdigit():
                year = int(arg)
            else:
                error_title = "Unable to parse command"
                error_message = 'Are you sure you used the proper format (ex: math-2060 2017 honors)?'

        if len(args) > 2:
            error_title = "Too many arguments"
            error_message = 'Are you sure you used the proper format (ex: math-2060 2017 honors)?'

        # Further processing of arguments
        if not self.grades_df.CourseId.str.contains(course).any():
            error_title = "Course doesn't exist"
            error_message = 'Are you sure you used the proper notation (ex: cpsc-2120)?'
        elif self.grades_df[(self.grades_df.CourseId == course)].Year.max() < year:
            error_title = "No data for year %s" % year
            error_message = 'There is no grade data for your course for this year onward; please extend the range and try again.'
        elif year < 2014:
            error_title = "Year below minimum"
            error_message = "The year you selected is below the minimum threshold (%d)." % MIN_YEAR

        if error_title:
            embed = discord.Embed(title="Grades", color=Colors.Error)
            embed.add_field(name="ERROR: " + error_title, value=error_message, inline=False)
            embed.add_field(name=f'Help:',
                            value=f'Run `{await self.bot.current_prefix(ctx)}help grades` for documentation or ' \
                                  f'`{await self.bot.current_prefix(ctx)}grades list` to find out which ' \
                                  'courses are available',
                            inline=False)
            return await ctx.send(embed=embed)

        # Default: no honors preference
        df = self.grades_df[(self.grades_df.CourseId == course) & (self.grades_df.Year >= year)]

        if honors == "honors":
            df = self.grades_df[
                (self.grades_df.CourseId == course) & (self.grades_df.Year >= year) & (self.grades_df.Honors == True)]
        elif honors == "non-honors":
            df = self.grades_df[(self.grades_df.CourseId == course) & (self.grades_df.Year >= year) & (
                    self.grades_df.Honors != True)]

        log.info(df)

        A = f'{int(df.A.mean().round(2) * 100)}%'
        B = f'{int(df.B.mean().round(2) * 100)}%'
        C = f'{int(df.C.mean().round(2) * 100)}%'
        D = f'{int(df.D.mean().round(2) * 100)}%'
        F = f'{int(df.F.mean().round(2) * 100)}%'
        W = f'{int(df.W.mean().round(2) * 100)}%'

        title = "Grades for %s since %d" % (course, year)

        if honors == "honors":
            title = "Grades for %s (Honors) since %d" % (course, year)
        elif honors == "non-honors":
            title = "Grades for %s (Non-Honors) since %d" % (course, year)

        embeds = []

        embed = discord.Embed(title=title, color=Colors.ClemsonOrange)
        embed.set_footer(text=self.get_full_name(ctx.author), icon_url=ctx.author.avatar_url)
        embed.description = title
        embed.add_field(name='Overall Distribution', value=f'```A: {A}\nB: {B}\nC: {C}\nD: {D}\nF: {F}\nW: {W}```')
        embed.add_field(name='Total Number of Classes Analyzed', value=str(len(df)), inline=False)
        embed.add_field(name='Total Number of Professors Found', value=str(len(df.groupby(['Instructor']))), inline=False)
        embed.add_field(name='Explanation',
                        value=f'Run `{await self.bot.current_prefix(ctx)}help grades` for more information on this command')
        embeds.append(embed)

        # group by the prof

        for i, row in df.groupby(['Instructor']).mean().iterrows():
            embed = discord.Embed(title=title, color=Colors.ClemsonOrange)
            embed.description = title
            embed.set_footer(text=self.get_full_name(ctx.author), icon_url=ctx.author.avatar_url)
            A = f'{int(row.A.round(2) * 100)}%'
            B = f'{int(row.B.round(2) * 100)}%'
            C = f'{int(row.C.round(2) * 100)}%'
            D = f'{int(row.D.round(2) * 100)}%'
            F = f'{int(row.F.round(2) * 100)}%'
            W = f'{int(row.W.round(2) * 100)}%'

            val = f'```A: {A}\nB: {B}\nC: {C}\nD: {D}\nF: {F}\nW: {W}```'
            embed.add_field(name=f"{row.name}'s distribution", value=val)
            embed.add_field(name='Total Number of Classes Analyzed', value=str(len(df)), inline=False)
            embed.add_field(name='Total Number of Professors Found', value=str(len(df.groupby(['Instructor']))),
                            inline=False)
            embed.add_field(name='Explanation',
                            value=f'Run `{await self.bot.current_prefix(ctx)}help grades` for more information on this command')
            embeds.append(embed)

        await self.bot.messenger.publish(Events.on_set_pageable_embed,
                                         pages=embeds,
                                         author=ctx.author,
                                         channel=ctx.channel,
                                         timeout=360)

    @ext.group(invoke_without_command=True, case_insensitive=True)
    @ext.long_help(
        """
        Attempts to give more information about professor's grade distribution at Clemson.
        
        General usage:
        `prof [name] (honors|non-honors|all)`
        
        Where `name` is required, but the `honors` argument is optional.
        
        Default `honors` argument: `all`

        DISCLAIMER:
        Not every professor listed will be at Clemson, this is a tool built for better information but not complete information.
        In addition, this system works on the Grade Distribution Releases located at https://www.clemson.edu/institutional-effectiveness/oir/data-reports/
        In Addition, Clemson provides incomplete and mangled professor data so there will be multiple different versions of the same professor. This is just a byproduct of how the data is distributed from the university
        """
    )
    @ext.short_help('Provides info about a given professor')
    @ext.example(('prof brian dean', 'prof kristi whitehead honors'))
    async def prof(self, ctx, *args):
        honors = ""
        if args[-1] in ("honors", "hon"):
            honors = "honors"
        elif args[-1] in ("non-honors", "non-hon", "regular", "normal"):
            honors = "non-honors"
        elif args[-1] == "all":
            honors = "all"

        if honors:
            # User specified correct honors attribute; prof name is all but last word
            prof = " ".join(args[:-1])
        else:
            # No honors argument (or incorrect), assume prof name is entire string
            prof = " ".join(args)

        if not self.grades_df.Instructor.str.contains(prof, case=False).any():
            embed = discord.Embed(title="Professors", color=Colors.Error)
            result = f'"{prof}" is not a known Professor\n'
            embed.add_field(name="ERROR: Professor doesn't exist", value=result, inline=False)
            embed.add_field(name=f'Help:',
                            value=f'Run `{await self.bot.current_prefix(ctx)}prof list` to find what professors are available',
                            inline=False)
            return await ctx.send(embed=embed)

        # check for if there is a 0% A rate, that means it was a pass fail class and we dont handle those
        df = self.grades_df[(self.grades_df.Instructor.str.lower() == prof.lower()) & (self.grades_df.A > 0)]

        # Honors/Non-honors logic
        if honors == "honors":
            df = self.grades_df[(self.grades_df.Instructor.str.lower() == prof.lower()) & (self.grades_df.A > 0) & (
                        self.grades_df.Honors == True)]
        elif honors == "non-honors":
            df = self.grades_df[(self.grades_df.Instructor.str.lower() == prof.lower()) & (self.grades_df.A > 0) & (
                        self.grades_df.Honors != True)]

        if df.empty:
            title = "Error: That professor has no available data"

            if honors == "honors":
                title = "Error: That professor has no available data for honors"
            elif honors == "non-honors":
                title = "Error: That professor has no available data for non-honors"

            embed = discord.Embed(title=title, color=Colors.Error)
            embed.add_field(name=f'Help:',
                            value=f"This professor's data might be under a different name, run `{await self.bot.current_prefix(ctx)}prof list` to find what professors are available",
                            inline=False)
            return await ctx.send(embed=embed)

        A = f'{int(df.A.mean().round(2) * 100)}%'
        B = f'{int(df.B.mean().round(2) * 100)}%'
        C = f'{int(df.C.mean().round(2) * 100)}%'
        D = f'{int(df.D.mean().round(2) * 100)}%'
        F = f'{int(df.F.mean().round(2) * 100)}%'
        W = f'{int(df.W.mean().round(2) * 100)}%'
        normalized_name = df.Instructor.any()

        title = f'Overall Grade Distribution for {normalized_name} across all classes taught'

        if honors == "honors":
            title = f'Overall Grade Distribution for {normalized_name} across all honors classes taught'
        elif honors == "non-honors":
            title = f'Overall Grade Distribution for {normalized_name} across all non-honors classes taught'

        embeds = []

        embed = discord.Embed(title=title,
                              color=Colors.ClemsonOrange)
        embed.set_footer(text=self.get_full_name(ctx.author), icon_url=ctx.author.avatar_url)
        embed.add_field(name='Overall Distribution', value=f'```A: {A}\nB: {B}\nC: {C}\nD: {D}\nF: {F}\nW: {W}```')
        embed.add_field(name='Total Number of Classes Analyzed', value=str(len(df.groupby(['CourseId']))), inline=False)
        embed.add_field(name='Explanation',
                        value=f'Run `{await self.bot.current_prefix(ctx)}help grades` for more information on this command')
        embeds.append(embed)

        title2 = f'Grade Distribution for {normalized_name}'

        if honors == "honors":
            title2 = f'Grade Distribution for {normalized_name} (Honors)'
        elif honors == "non-honors":
            title2 = f'Grade Distribution for {normalized_name} (Non-Honors)'

        for i, row in df.groupby(['CourseId']).mean().iterrows():
            embed = discord.Embed(title=title2, color=Colors.ClemsonOrange)
            embed.set_footer(text=self.get_full_name(ctx.author), icon_url=ctx.author.avatar_url)
            A = f'{int(row.A.round(2) * 100)}%'
            B = f'{int(row.B.round(2) * 100)}%'
            C = f'{int(row.C.round(2) * 100)}%'
            D = f'{int(row.D.round(2) * 100)}%'
            F = f'{int(row.F.round(2) * 100)}%'
            W = f'{int(row.W.round(2) * 100)}%'

            val = f'```A: {A}\nB: {B}\nC: {C}\nD: {D}\nF: {F}\nW: {W}```'
            embed.add_field(name=f"{row.name}'s distribution", value=val)
            embed.add_field(name='Total Number of Classes Analyzed', value=str(len(df)), inline=False)
            embed.add_field(name='Explanation',
                            value=f'Run `{await self.bot.current_prefix(ctx)}help grades` for more information on this command')
            embeds.append(embed)

        await self.bot.messenger.publish(Events.on_set_pageable_embed,
                                         pages=embeds,
                                         author=ctx.author,
                                         channel=ctx.channel,
                                         timeout=360)

    def get_courses(self):
        grades = self.grades_df.groupby(['CourseId']).mean().iterrows()

        embeds = []

        # begin generating paginated columns
        for chunk in self.chunk_list([prof.name for i, prof in grades], 51):

            # we need to create the columns on the page so chunk the list again
            content = ''
            for col in self.chunk_list(chunk, 3):
                # the columns wont have the perfect number of elements every time, we need to append spaces if
                # the list entries is less then the number of columns
                while len(col) < 3:
                    col.append(' ')

                # Cocatenate the formatted column string to the page content string
                content += "{: <12} {: <12} {: <12}\n".format(*col)

            # Apped the content string to the list of pages to send to the paginator
            # Marked as a code block to ensure a monospaced font and even columns

            embed = discord.Embed(title='All Known Courses', color=Colors.ClemsonOrange)
            embed.add_field(name='Listings:', value=f'```{content}```')
            embed.add_field(name='Info:',
                            value=f'Clemson provides incomplete and mangled data so there may be different versions of the same course, as well as other mangled names. This is just a byproduct of how the data is distributed by the university',
                            inline=False)

            embeds.append(embed)
        return embeds

    @grades.command(aliases=['list'])
    @ext.long_help(
        'Lists all available Courses, some Courses will just be a name with no data'
    )
    @ext.short_help('Lists all courses')
    @ext.example('grades list')
    async def list_grades(self, ctx):
        await self.bot.messenger.publish(Events.on_set_pageable_embed,
                                         pages=self.all_courses,
                                         author=ctx.author,
                                         channel=ctx.channel,
                                         timeout=360)

    def get_profs(self):
        profs = self.grades_df.groupby(['Instructor']).mean().iterrows()

        embeds = []

        # begin generating paginated columns
        # chunk the list of tags into groups of TAG_CHUNK_SIZE for each page
        for chunk in self.chunk_list([prof.name for i, prof in profs], TAG_CHUNK_SIZE):

            # we need to create the columns on the page so chunk the list again
            content = ''
            for col in self.chunk_list(chunk, 2):
                # the columns wont have the perfect number of elements every time, we need to append spaces if
                # the list entries is less then the number of columns
                while len(col) < 3:
                    col.append(' ')

                # Cocatenate the formatted column string to the page content string
                content += "{: <24}  {: <24}\n".format(*col)

            # Apped the content string to the list of pages to send to the paginator
            # Marked as a code block to ensure a monospaced font and even columns
            embed = discord.Embed(title='All Known Professors', color=Colors.ClemsonOrange)
            embed.add_field(name='Listings:', value=f'```{content}```')
            embed.add_field(name='Info:',
                            value=f'Clemson provides incomplete and mangled data so there may be multiple different versions of the same professor as well as other manglaed names. This is just a byproduct of how the data is distributed by the university',
                            inline=False)

            embeds.append(embed)
        return embeds

    @prof.command(aliases=['list'])
    @ext.long_help(
        'Lists all available professors, some professors will just be a name with no data'
    )
    @ext.short_help('Lists all professors')
    @ext.example('prof list')
    async def list_prof(self, ctx):
        await self.bot.messenger.publish(Events.on_set_pageable_embed,
                                         pages=self.all_profs,
                                         author=ctx.author,
                                         channel=ctx.channel,
                                         timeout=360)

    def get_full_name(self, author) -> str:
        return f'{author.name}#{author.discriminator}'

    def chunk_list(self, lst, n):
        """Yield successive n-sized chunks from lst."""
        for i in range(0, len(lst), n):
            yield lst[i:i + n]


def setup(bot):
    bot.add_cog(GradesCog(bot))
