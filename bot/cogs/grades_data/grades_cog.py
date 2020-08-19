import json
import os

import logging
import random
import time

import discord
import discord.ext.commands as commands

from bot.consts import Colors

log = logging.getLogger(__name__)

class gradesCog(commands.Cog):
    special_converted_files = ['2018Fall.csv', '2018Spring.csv'] 
    #these files have special formatting for names 
    #(ie ' "Smith, John William" ' is normal and in these it's simply 'Smith John William' without commas or quotes )

    converted_files = ['2013Fall.csv', 
                    '2014Spring.csv', 
                    '2014Fall.csv', 
                    '2015Spring.csv', 
                    '2015Fall.csv', 
                    '2016Spring.csv', 
                    '2016Fall.csv', 
                    '2017Spring.csv', 
                    '2017Fall.csv', 
                    '2019Spring.csv', 
                    '2019Fall.csv', 
                    '2020Spring.csv']

    def __init__(self, bot):
        self.bot = bot
        self.fileLines = []
        self.master_list = {}
        self.master_prof_list = {}

    def process_Search(self, orig_query: str) -> str: #Primary search function and processing for a query. A query is generally defined by 
                                    #"Course-Number" of which it pulls the data from the DB.
        
        query = orig_query.upper()
        
        items = query.split('-')
        master_String = ''

        if query in self.master_list:
            data_list = self.master_list[query]
        else:
            raise NotADirectoryError

        # Get the most recent course name on file. 
        # If we did the beginning, it'd throw the incorrect name because Clemson is big dumb.
        name = data_list[-1]['name']

        # print(data_list)
        a = []
        b = []
        c = []
        d = []
        f = []
        w = []
        p = []
        np = []
        professorGrades = {}

        for i in data_list:
            a.append(i['A'])
            b.append(i['B'])
            c.append(i['C'])
            d.append(i['D'])
            f.append(i['F'])
            w.append(i['W'])

            searchableName = self.getFirstLast(i['Professor'])
            professorGrades[searchableName] = []

        gradesList = (a,b,c,d,f,w,p,np)
        
        for letterGrade in gradesList:
            for i in range(len(letterGrade)):
                letterGrade[i] = int(letterGrade[i][:-1])

        AvgA = sum(a) // len(a)
        AvgB = sum(b) // len(b)
        AvgC = sum(c) // len(c)
        AvgD = sum(d) // len(d)
        AvgF = sum(f) // len(f)
        AvgWithdraw = sum(w) // len(w)

        courseString = f"""Average; 
                        A: {AvgA}%
                        B: {AvgB}%
                        C: {AvgC}%
                        D: {AvgD}%
                        F: {AvgF}%
                        W: {AvgWithdraw}%
                        from {len(data_list)} class(es) for {orig_query}: {name}
                        """
        #Professor name to go in professor string
        bestProfName = '' 
        bestProfAB = 0
        bestProfLenCount = 0

        worstProfName = ''
        worstProfDFW = 0
        worstProfLenCount = 0

        data = []

        for i in professorGrades:
            
            try:
                professorGrades[i].extend(self.process_profQuery(i))
                data = professorGrades[i]
            except Exception as e:
                print(e)
            
            if data[0] > bestProfAB:
                bestProfName = i
                bestProfAB = data[0]
                bestProfLenCount = data[-1]
            if data[1] > worstProfDFW:
                worstProfName = i
                worstProfDFW = data[1]
                worstProfLenCount = data[-1]
        bestProfName = bestProfName.replace('"','')
        worstProfName = worstProfName.replace('"', '')

        profString = f'The statistically best professor is {bestProfName} with an A+B Avg of {bestProfAB}% in {bestProfLenCount} classes\n\nThe statistically worst professor is {worstProfName} with an D+F+W Avg of {worstProfDFW}% out of {worstProfLenCount} class(es)'

        return courseString + '\n\n' + profString + '\n\n'

    def getInitials(self, Name):
        initials = ''
        Name = Name.split()
        Name = Name[1:] + [Name[0]]
        for i in Name:
            initials += i[0]
        return initials

    def initialize(self):
        #SKIP PARSE DATA WHEN NOT NECESSARY
        if os.path.isfile('bot/cogs/grades_data/assets/master.json'): 
            with open('bot/cogs/grades_data/assets/master.json', 'r') as f:
                self.master_list = json.load(f)
        
            if os.path.isfile('bot/cogs/grades_data/assets/master_prof.json'):
                with open('bot/cogs/grades_data/assets/master_prof.json', 'r') as f:
                    self.master_prof_list = json.load(f)
            
        else:
            notFound = ''
            
            if not os.path.isfile('bot/cogs/grades_data/assets/master.json'): 
                notFound += 'master.json'
            
            if not os.path.isfile('bot/cogs/grades_data/assets/master_prof.json'):
                notFound += 'master_prof.json'

            log.error(f'{notfound} file not found, aborting grades command')
            
            raise FileNotFoundError(notFound)
            
    def getFirstLast(self, Name):
        fml = Name.split()
        First = fml[1]
        Last = fml[0]
        return First + ' ' + Last

    def process_profQuery(self, Name):
        
        data_list = self.master_prof_list[Name]
        
        a = []
        b = []
        f = []
        w = []
        p = []
        np = []    

        c = []
        d = [] # Incase you want these 

        for i in data_list:
            a.append(i['A'])
            b.append(i['B'])
            c.append(i['C'])
            d.append(i['D'])
            f.append(i['F'])
            w.append(i['W'])
        gradesList = (a, b, c, d, f, w, p, np)
        for letterGrade in gradesList:
            for i in range(len(letterGrade)):
                letterGrade[i] = int(letterGrade[i][:-1])

        avg_a = sum(a) // len(a)
        avg_b = sum(b) // len(b)
        avg_c = sum(c) // len(c)
        avg_d = sum(d) // len(d)
        avg_f = sum(f) // len(f)
        avg_withdraw = sum(w) // len(w)

        return [(avg_a + avg_b), (avg_f + avg_withdraw), (len(data_list))]

    def toCamelCase(self, Name):
        items = Name.split()
        for i in range(len(items)):
            items[i] = items[i][0].upper() + items[i][1:].lower()
        return ' '.join(items)

    def searchCourse(self, query):
        string = ''
        string += 'Since Spring 2014, there is an ' + self.process_Search(query)
        
        return string
        
    def go(self, course):
        self.initialize()
        
        return self.searchCourse(course)

    @commands.command()
    async def grades(self, ctx, course):

        '''
        Attempts to give more information about courses @ Clemson.

        USE:

        grades <course title>-<course number>
        EX: !grades cpsc-1010

        DISCLAIMER:
        Not every professor listed will be at Clemson, this is a tool built for better information but not complete information
        In addition, this system works on the Grade Distribution Releases located at https://www.clemson.edu/institutional-effectiveness/oir/data-reports/
        *Course Sections that meet the following conditions are not included: Undergraduate classes with less than 10 students or Graduate classes with less than 5 students. In addition, if a section has all but 1 student making a common grade (example: All but one student makes a "B" in a class), the section is excluded.*
        '''
        
        try:
            embed = discord.Embed(title="Grades", color=Colors.ClemsonOrange)
            result = self.go(course)
            embed.add_field(name="Result", value=result, inline=False)
            prefix = await self.bot.get_prefix(ctx)
            if isinstance(prefix, list):
                prefix = prefix[0]
            exp = f'Type `{prefix}help grades` for more information' # NOQA
            embed.add_field(name='Explanation', value=exp)

        except NotADirectoryError: # output if course doesn't exist
            embed = discord.Embed(title="Grades", color=Colors.Error)
            result = 'That\'s not a course\n Are you sure you used the proper notation (ex: cpsc-2120)'
            embed.add_field(name="ERROR: Course doesn't exist", value=result, inline=False)
        
        except FileNotFoundError:
            embed = discord.Embed(title="Grades", color=Colors.Error)
            result = "Either master.json or master_prof.json are not found in the proper directory"
            embed.add_field(name="ERROR: File not found", value=result, inline=False)



        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(gradesCog(bot))