from typing import Generator, Sequence, TypeVar
from datetime import datetime
import arrow
from dateutil.relativedelta import relativedelta

from bot.utils.converters import DurationDelta, FutureDuration, PastDuration

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


def format_duration(duration: FutureDuration | PastDuration) -> str:
    """
    Formats the given datetime to a string.
    Uses relativedelta to calculate the difference between datetime.utcnow()
    and the given datetime and formats it as:
    A Year(s) B Month(s) C Week(s) D Day(s) E Hour(s) F Minute(s) G Second(s)
    """
    now = datetime.utcnow()
    delta = relativedelta(now, duration) if duration < now else relativedelta(duration, now)  # type: ignore
    s = ""
    if delta.years > 0:
        s += f'{delta.years} Year{"s" if delta.years > 1 else ""} '
    if delta.months > 0:
        s += f'{delta.months} Month{"s" if delta.months > 1 else ""} '
    if delta.weeks > 0:
        s += f'{delta.weeks} Week{"s" if delta.weeks > 1 else ""}'
    if delta.days > 0:
        s += f'{delta.days} Day{"s" if delta.days > 1 else ""} '
    if delta.hours > 0:
        s += f'{delta.hours} Hour{"s" if delta.hours > 1 else ""} '
    if delta.minutes > 0:
        s += f'{delta.minutes} Minute{"s" if delta.minutes > 1 else ""} '
    if delta.seconds > 0:
        s += f'{delta.seconds} Second{"s" if delta.seconds > 1 else ""}'
    return s
