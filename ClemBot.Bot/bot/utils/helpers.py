import calendar
import string
from datetime import datetime
from typing import Annotated, Generator, Iterator, Literal, Sequence, TypeVar

import arrow
from dateutil.relativedelta import relativedelta

from bot.utils.converters import FutureDuration, PastDuration

T = TypeVar("T")


def chunk_sequence(sequence: Sequence[T], chunk_size: int) -> Generator[Sequence[T], None, None]:
    """Yield successive chunks from the passed sequence."""

    for i in range(0, len(sequence), chunk_size):
        yield sequence[i : i + chunk_size]


def format_datetime(time: datetime) -> str:
    """
    Formats the given datetime to a string.
    Used for converting Python's datetime to C#'s DateTime.
    """
    return time.strftime("%Y-%m-%dT%H:%M:%S.%f")


def format_duration(
    duration: Annotated[datetime | relativedelta, FutureDuration | PastDuration],
) -> str:
    """
    Formats the given datetime to a string.
    Uses relativedelta to calculate the difference between datetime.utcnow()
    and the given datetime and formats it as:
    A Year(s) B Month(s) C Week(s) D Day(s) E Hour(s) F Minute(s) G Second(s)
    """
    if isinstance(duration, datetime):
        if duration < datetime.utcnow():
            delta = relativedelta(datetime.utcnow(), duration)
        else:
            delta = relativedelta(duration, datetime.utcnow())
    else:  # duration isinstance relativedelta
        delta = duration
        duration = datetime.utcnow() + duration
    arrow_date = arrow.get(duration)
    granularity = _get_timedelta_granularity(delta, 3)
    return arrow_date.humanize(only_distance=True, granularity=granularity)  # type: ignore


def _get_timedelta_granularity(delta: relativedelta, granularity: int) -> list[str]:
    def get_timedelta_granularity() -> Iterator[str]:
        if delta.years >= 1:
            yield "year"

        if delta.months >= 1:
            yield "month"

        if delta.weeks >= 1:
            yield "week"

        if delta.days >= 1:
            yield "day"

        if delta.hours >= 1:
            yield "hour"

        if delta.minutes >= 1:
            yield "minute"

        if delta.seconds >= 1:
            yield "second"

    return list(get_timedelta_granularity())[:granularity]


def as_timestamp(date: datetime, /, style: Literal["f", "F", "d", "D", "t", "T", "R"] = "f") -> str:
    """
    Formats the given datetime to a Discord timestamp.
    Used over discord.utils.format_dt due to incorrect timestamp output.
    """
    timestamp = calendar.timegm(date.utctimetuple())
    return f"<t:{timestamp}:{style}>"


def contains_whitespace(s: str) -> bool:
    """
    Checks if the given string contains any whitespace characters.
    Checks against `string.whitespace` to look for whitespace.
    Returns True if the given string contains whitespace, False otherwise.
    """
    return any(c in s for c in string.whitespace)
