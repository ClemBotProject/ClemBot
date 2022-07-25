import re
import typing as t
from datetime import datetime

import arrow
from dateutil.relativedelta import relativedelta
from discord.ext.commands import Context, Converter
from discord.ext.commands.errors import ConversionError
from discord.ext.commands.errors import UserInputError
from bot.consts import Claims
from bot.errors import ConversionError

"""
This converter code was copied from the python discord bot
https://github.com/python-discord/bot/blob/master/bot/converters.py
"""


class DurationDelta(Converter):
    """Convert duration strings into dateutil.relativedelta.relativedelta objects."""

    duration_parser = re.compile(
        r"((?P<years>\d+?) ?(years|year|Y|y) ?)?"
        r"((?P<months>\d+?) ?(months|month|M) ?)?"
        r"((?P<weeks>\d+?) ?(weeks|week|W|w) ?)?"
        r"((?P<days>\d+?) ?(days|day|D|d) ?)?"
        r"((?P<hours>\d+?) ?(hours|hour|hr|H|h) ?)?"
        r"((?P<minutes>\d+?) ?(minutes|minute|min|m) ?)?"
        r"((?P<seconds>\d+?) ?(seconds|second|sec|S|s))?"
    )

    async def convert(self, ctx: Context, duration: str) -> relativedelta:
        """
        Converts a `duration` string to a relativedelta object.
        The converter supports the following symbols for each unit of time:
        - years: `Y`, `y`, `year`, `years`
        - months: `M`, `month`, `months`
        - weeks: `w`, `W`, `week`, `weeks`
        - days: `d`, `D`, `day`, `days`
        - hours: `H`, `h`, `hour`, `hours`
        - minutes: `m`, `min`, `minute`, `minutes`
        - seconds: `S`, `sec`, `s`, `second`, `seconds`
        The units need to be provided in descending order of magnitude.
        """
        match = self.duration_parser.fullmatch(duration)
        if not match:
            raise ConversionError(f"`{duration}` is not a valid duration string.")

        duration_dict = {unit: int(amount) for unit, amount in match.groupdict(default=0).items()}
        delta = relativedelta(**duration_dict)

        return delta


class Duration(DurationDelta):
    """Convert duration strings into UTC datetime.datetime objects."""

    def __init__(self, ctx: Context, duration: t.Union[str, relativedelta]):
        self.ctx = ctx
        self.duration = duration
        if isinstance(duration, relativedelta):
            self.delta = duration
        else:  # super.convert() is an async method - this is not
            match = self.duration_parser.fullmatch(duration)
            if not match:
                raise ConversionError(f'`{duration}` is not a valid duration string.')
            duration_dict = {unit: int(amount) for unit, amount in match.groupdict(default=0).items()}
            self.delta = relativedelta(**duration_dict)

    def as_future(self) -> datetime:
        """
        Converts a `duration` string to a datetime object that's `duration` is in the future.
        The converter supports the same symbols for each unit of time as its parent class.
        """
        now = datetime.utcnow()
        try:
            return now + self.delta
        except ValueError:
            raise ConversionError(f'`{self.duration}` results in a datetime outside of the supported range.')

    def as_past(self) -> datetime:
        """
        Converts a `duration` string to a datetime object that's `duration` is in the past.
        The converter supports the same symbols for each unit of time as its parent class.
        """
        now = datetime.utcnow()
        try:
            return now - self.delta
        except ValueError:
            raise ConversionError(f'`{self.duration}` results in a datetime outside of the supported range.')

    def __str__(self):
        return arrow.get(datetime.utcnow() + self.delta).humanize(only_distance=True)


class ClaimsConverter(Converter):
    """Convert a given claim string into its enum representation"""

    async def convert(self, ctx: Context, claim: str) -> Claims:
        try:
            return Claims.__members__[claim]
        except KeyError:
            raise ConversionError(f'`{claim}` is not a valid Claim')


class HonorsConverter(Converter):
    """Sanitize honors argument input for grades_cog"""

    async def convert(self, ctx: Context, argument: str) -> str:
        honors = None

        if argument in ('honors', 'hon', 'h'):
            honors = 'honors'
        elif argument in ('non-honors', 'non-hon', 'regular', 'normal', 'nh'):
            honors = 'non-honors'
        elif argument in ('all', 'a'):
            honors = 'all'
        else:
            raise ConversionError()

        return honors


def trivia_cog_converter(input_length, input_list): #converts the args as fast as possible 

        url_parameters = []

        for i in range (0, input_length):
            match i:  #Revolves around beautiful O(1) based indexing
                case 0: # question number
                    if input_list[0].isnumeric():
                        question_number = int(input_list[0])
                        if 0 < question_number <= 50:
                             url_parameters.append(question_number)
                        else:
                            raise UserInputError(
                                "Question Number entered is out of range!")
                    else:
                        raise UserInputError(
                            "Question Number has to be a number within the range of 1 to 50")
                case 1: #category
                    if input_list[1].isnumeric():
                        trivia_number = int(input_list[1])
                        if 0 < trivia_number <= 24:
                            url_parameters.append(trivia_number + 8)
                        elif trivia_number == 0: # special number to allow entry of empty arguments since it would be impossible otherwise
                            url_parameters.append(None)
                        else:
                            raise UserInputError(
                                "Category Number out of bounds(Number has to be 1-24) or enter the category you want! Type ?trivia help to see the category list")
                    else:
                        trivia_category = input_list[1].lower()

                        for x in CATEGORYLIST_LOWER:
                            if x.find(trivia_category) != -1:
                                return_this = CATEGORYLIST_LOWER.index(x) + 9
                                url_parameters.append(return_this)
                                break;
                        else:
                            raise UserInputError("Category not found!")
                case 2: #difficulty
                    if input_list[2].isnumeric():
                        evaluate_int = int(input_list[2])
                        if 0 < evaluate_int <= 3:
                            return_string = DIFFICULTY_LOWER[evaluate_int - 1]
                            url_parameters.append(return_string)
                        elif evaluate_int == 0:
                            url_parameters.append(None)
                        else:
                            raise UserInputError(
                                "Difficulty Number out of bounds(Number has to be 1-3) or enter Easy-Hard! Type ?trivia help to see the difficulty list.")
                    else:
                        difficulty = input_list[2].lower()
                        for x in DIFFICULTY_LOWER:

                            if (x.find(difficulty) != -1):  #Searches the substring. If this ever comes up, its not a bug you can type in a and not find your category GIGO. It is better than exact case parsing.
                                url_parameters.append(x)
                                break;
                        else:
                            raise UserInputError("Difficulty not found")
                case 3: #question type
                    if input_list[3].isnumeric():
                        evaluate_int = int(input_list[3])
                        if 0 < evaluate_int < 3:
                            final_return = QUESTIONTYPE[evaluate_int - 1]
                            url_parameters.append(final_return)
                        elif evaluate_int == 0:
                            url_parameters.append(None)
                        else:
                            raise UserInputError(
                                "Question type number out of bounds(1 or 2) 1: Multiple Choice 2: Boolean. Type ?trivia help to see our question types.")
                    else:
                        question_type = input_list[3].lower()
                        for x in QUESTIONTYPE:
                            if (x.find(question_type) != -1):
                               url_parameters.append(x)
                               break;
                        else:
                            raise UserInputError(
                                "Couldn't find the question type you are looking for!.")
        
        url = URL_BUILDER + str(url_parameters[0]) #This has to exist or else it would have raised an exception and exited

        for x in range (1, input_length):
            if url_parameters[x]:
                match x:
                    case 1:
                       url= (f"{url}&category={str(url_parameters[1])}")
                    case 2:
                        url = (f"{url}&difficulty={url_parameters[2]}")
                    case 3:
                        url = (f"{url}&type={url_parameters[input_length-1]}")
        return url


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
