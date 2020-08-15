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
    special_converted_files = ['2018Fall.csv','2018Spring.csv'] #these files have special formatting for names (ie ' "Smith, John William" ' is normal and in these it's simply 'Smith John William' without commas or quotes )
    #TBH, this is the easier way to parse but whatevs
    converted_files = ['2013Fall.csv', '2014Spring.csv', '2014Fall.csv', '2015Spring.csv', '2015Fall.csv', '2016Spring.csv', '2016Fall.csv', '2017Spring.csv', '2017Fall.csv', '2019Spring.csv', '2019Fall.csv', '2020Spring.csv']

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

        name = data_list[-1]['name'] # Get the most recent course name on file. If we did the beginning, it'd throw the incorrect name because Clemson is big dumb.
        # print(data_list)
        A = []
        B = []
        C = []
        D = []
        F = []
        W = []
        P = []
        NP = []
        professorGrades = {}

        for i in data_list:
            A.append(i['A'])
            B.append(i['B'])
            C.append(i['C'])
            D.append(i['D'])
            F.append(i['F'])
            W.append(i['W'])

            searchableName = self.getFirstLast(i['Professor'])
            professorGrades[searchableName] = []

        gradesList = (A,B,C,D,F,W,P,NP)
        
        for letterGrade in gradesList:
            for i in range(len(letterGrade)):
                letterGrade[i] = int(letterGrade[i][:-1])

        AvgA = sum(A)//len(A)
        AvgB = sum(B)//len(B)
        AvgC = sum(C)//len(C)
        AvgD = sum(D)//len(D)
        AvgF = sum(F)//len(F)
        AvgWithdraw = sum(W)//len(W)

        courseString = f'Average; \nA: {AvgA}%\nB: {AvgB}%\nC: {AvgC}%\nD: {AvgD}%\nF: {AvgF}%\nW: {AvgWithdraw}%\nfrom {len(data_list)} class(es) for {orig_query}: {name}'

        bestProfName = '' #Professor name to go in professor string
        bestProfAB = 0
        bestProfLenCount = 0

        worstProfName = ''
        worstProfFW = 0
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
            if data[1] > worstProfFW:
                worstProfName = i
                worstProfFW = data[1]
                worstProfLenCount = data[-1]
        bestProfName = bestProfName.replace('"','')
        worstProfName = worstProfName.replace('"', '')

        profString = f'The statistically best professor is {bestProfName} with an A+B Avg of {bestProfAB}% in {bestProfLenCount} classes\n\nThe statistically worst professor is {worstProfName} with an F+W Avg of {worstProfFW}% out of {worstProfLenCount} class(es)'

        return courseString + '\n\n' + profString + '\n\n'

    def getInitials(self, Name):
        initials = ''
        Name = Name.split()
        Name = Name[1:] + [Name[0]] #Rotates it
        for i in Name:
            initials += i[0]
        return initials

    def initialize(self):

        if os.path.isfile('bot/cogs/grades_data/assets/master.json'): #SKIP PARSE DATA WHEN NOT NECESSARY
            with open('bot/cogs/grades_data/assets/master.json', 'r') as f:
                self.master_list = json.load(f)
        
            if os.path.isfile('bot/cogs/grades_data/assets/master_prof.json'):
                with open('bot/cogs/grades_data/assets/master_prof.json', 'r') as f:
                    self.master_prof_list = json.load(f)
            
        else:
            log.info('FILES NOT FOUND')
            
            

    def getFirstLast(self, Name):
        FML = Name.split()
        First = FML[1]
        Last = FML[0]
        return First + ' ' + Last

    def process_profQuery(self, Name):
        
        data_list = self.master_prof_list[Name]
        
        A = []
        B = []
        F = []
        W = []
        P = []
        NP = []    

        C = []
        D = [] # Incase you want these 

        for i in data_list:
            A.append(i['A'])
            B.append(i['B'])
            C.append(i['C'])
            D.append(i['D'])
            F.append(i['F'])
            W.append(i['W'])
        gradesList = (A,B,C,D,F,W,P,NP)
        for letterGrade in gradesList:
            for i in range(len(letterGrade)):
                letterGrade[i] = int(letterGrade[i][:-1])

        AvgA = sum(A)//len(A)
        AvgB = sum(B)//len(B)
        AvgC = sum(C)//len(C)
        AvgD = sum(D)//len(D)
        AvgF = sum(F)//len(F)
        AvgWithdraw = sum(W)//len(W)

        return  [(AvgA + AvgB), (AvgF+AvgWithdraw), (len(data_list))]

    def toCamelCase(self, Name):
        items = Name.split()
        for i in range(len(items)):
            items[i] = items[i][0].upper() + items[i][1:].lower()
        return " ".join(items)

    def searchCourse(self, query):
        string = ""
        string += 'Since Spring 2014, there is an ' + self.process_Search(query)
        string += 'DISCLAIMER:\n'
        string += 'Not every professor listed will be at Clemson, this is a tool built for better information but not complete information\n'
        string += '\nIn addition, this system works on the Grade Distribution Releases located at https://www.clemson.edu/institutional-effectiveness/oir/data-reports/\n'
        string += 'Limitations GDR are as follows:\n'

        string += '*Course Sections that meet the following conditions are not included: Undergraduate classes with less than 10 students or Graduate classes with less than 5 students. In addition, if a section has all but 1 student making a common grade (example: All but one student makes a "B" in a class), the section is excluded.*'
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
        '''
        
        try:
            embed = discord.Embed(title="Grades", color=Colors.ClemsonOrange)
            result = self.go(course)
            result = result[:1024]

        except NotADirectoryError as e: # output if course doesn't exist
            embed = discord.Embed(title="Grades", color=Colors.Error)
            result = 'That\'s not a course\n Are you sure you used the proper notation (ex: cpsc-2120)'
            embed.add_field(name="ERROR", value=result, inline=False)

        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(gradesCog(bot))