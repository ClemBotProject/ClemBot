from datetime import datetime
from typing import Generator, Sequence, TypeVar

T = TypeVar("T")


def chunk_sequence(sequence: Sequence[T], chunk_size: int) -> Generator[Sequence[T], None, None]:
    """Yield successive chunks from the passed sequence."""

    for i in range(0, len(sequence), chunk_size):
        yield sequence[i: i + chunk_size]


def parse_datetime(time: str) -> datetime:
    return datetime.strptime(time, '%Y-%m-%dT%H:%M:%S.%f')


def format_datetime(time: datetime) -> str:
    return time.strftime('%Y-%m-%dT%H:%M:%S.%f')
