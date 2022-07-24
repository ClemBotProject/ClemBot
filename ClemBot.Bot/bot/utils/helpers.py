from datetime import datetime
from typing import Generator, Sequence, TypeVar

T = TypeVar("T")


def chunk_sequence(sequence: Sequence[T], chunk_size: int) -> Generator[Sequence[T], None, None]:
    """Yield successive chunks from the passed sequence."""

    for i in range(0, len(sequence), chunk_size):
        yield sequence[i: i + chunk_size]


def parse_datetime(time: str) -> datetime:
    """
        Parses the given string to a datetime.
        Used for converting C#'s DateTime to Python's datetime.
    """
    return datetime.strptime(time, '%Y-%m-%dT%H:%M:%S.%f')


def format_datetime(time: datetime) -> str:
    """
        Formats the given datetime to a string.
        Used for converting Python's datetime to C#'s DateTime.
    """
    return time.strftime('%Y-%m-%dT%H:%M:%S.%f')
