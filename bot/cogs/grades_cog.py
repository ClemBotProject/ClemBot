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
        print("PROCESSING")
        query = orig_query.upper()
        
        items = query.split("-")
        master_String = ''

        # if("ALL" in items):
        #     print("ALL IN QUERY")
        #     print("HERE COMES THE SUN")
        #     if items[0] == "ALL" and items[1] == "ALL":
        #         print("ALLALL")
        #         for i in master_list:
        #             master_String += process_Search(i)
        #     elif items[0] == "ALL":
        #         for i in master_list:
        #             if items[1] in i:
        #                 master_String += process_Search(i)
        #     elif items[1] == "ALL":
        #         for i in master_list:
        #             if items[0] in i:
        #                 master_String += process_Search(i)
        #     else:
        #         print("Misunderstood")
        #         return "HELP"
        #     return master_String

        # else:
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

        courseString = "Average; A: {}%\nB: {}%\nC: {}%\nD: {}%\nF: {}%\nW: {}%\nfrom {} class(es) for {}: {}".format(AvgA, AvgB, AvgC, AvgD, AvgF, AvgWithdraw, len(data_list), orig_query, name)
        

        bestProfName = "" #Professor name to go in professor string
        bestProfAB = 0
        bestProfLenCount = 0

        worstProfName = ""
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
        
        profString = "The statistically best professor is {} with an A+B Avg of {}% in %s classes\n\nThe statistically worst professor is {} with an F+W Avg of {}% out of {} class(es)".format(bestProfName, bestProfAB, bestProfLenCount, worstProfName, worstProfFW, worstProfLenCount) #Final professor string

        return courseString + "\n\n" + profString + "\n\n"

    def getInitials(self, Name):
        initials = ""
        Name = Name.split()
        Name = Name[1:] + [Name[0]] #Rotates it
        for i in Name:
            initials += i[0]
        return initials

    def initialize(self):

        if os.path.isfile('bot/cogs/Student-Teacher/assets/master.json'): #SKIP PARSE DATA WHEN NOT NECESSARY
            print("FOUND COURSE FILE")
            with open('bot/cogs/Student-Teacher/assets/master.json', 'r') as f:
                self.master_list = json.load(f)
            # print(master_list)
            if os.path.isfile('bot/cogs/Student-Teacher/assets/master_prof.json'):
                print("FOUND PROF FILE")
                with open('bot/cogs/Student-Teacher/assets/master_prof.json', 'r') as f:
                    self.master_prof_list = json.load(f)
            else:
                print("PROF FILE NOT FOUND")
        else:
            print("FILE NOT FOUND PLEASE SEND HELP")
            
            

    def getFirstLast(self, Name):
        FML = Name.split()
        First = FML[1]
        Last = FML[0]
        return First + " " + Last

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

    def getAllCourses(self):
        temp = []
        for i in self.master_list:
            if i[:-5] not in temp:
                temp.append(i[:-5])
            else:
                pass
        with open("bot/cogs/Student-Teacher/assets/CourseList.txt", "w") as f:
            for i in range(len(temp)):
                f.write(temp[i]+"\n")

    def searchCourse(self, query):
        # query = input("What course do you want to search? (Format: <Course>-<number> ie CPSC-3720)\n")
        string = ""
        # try:
            
        # string += "\n--------------------------------------------------------\n"
        string += "Since Spring 2014, there was an average of " + self.process_Search(query)
        string += "DISCLAIMER:\n"
        string += "Not every professor listed will be at Clemson, this is a tool built for better information but not complete information\n"
        # string += "Take it at your own discression\n"
        # string += "\nIn addition, this system works on the Grade Distribution Releases located at https://www.clemson.edu/institutional-effectiveness/oir/data-reports/\n"
        # string += "As a result, the limitations according to the GDR are as follows:\n"
        string += '*Course Sections that meet the following conditions are not included: Undergraduate classes with less than 10 students or Graduate classes with less than 5 students. In addition, if a section has all but 1 student making a common grade (example: All but one student makes a "B" in a class), the section is excluded.*'
        # string += '\n----------------------------------------------------------------------------'
        return string
        # except NotADirectoryError as e:
        #     print("Class not found, are you sure you used the correct format? (Ex: cpsc-2120)")
        
        # except Exception as e:
        #     print("Something went wrong somewhere, idk bout that")
        #     print(e)

    def go(self, course):
        self.initialize()
        self.getAllCourses()
        return self.searchCourse(course)

    @commands.command()
    async def grades(self, ctx, course):
        
        try:
            embed = discord.Embed(title="Grades", color=Colors.ClemsonOrange)
            result = self.go(course)
            embed.add_field(name="Result", value=result, inline=False)
        except NotADirectoryError as e:
            embed = discord.Embed(title="Grades", color=Colors.Error)
            result = "That's not a course\n Are you sure you used the proper notation (ex: cpsc-2120)"
            embed.add_field(name="ERROR", value=result, inline=False)

        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(gradesCog(bot))