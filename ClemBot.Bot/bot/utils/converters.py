import re
import typing as t
from datetime import datetime

from dateutil.relativedelta import relativedelta
from discord.ext.commands import Context, Converter
from discord.ext.commands.errors import ConversionError

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

    async def convert(self, ctx: Context, duration: t.Union[str, relativedelta]) -> datetime:
        """
        Converts a `duration` string to a datetime object that's `duration` in the future.
        The converter supports the same symbols for each unit of time as its parent class.
        """
        delta = duration if isinstance(duration, relativedelta) else await super().convert(ctx, duration)
        now = datetime.utcnow()

        try:
            return now + delta
        except ValueError:
            raise ConversionError(f"`{duration}` results in a datetime outside the supported range.")


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
