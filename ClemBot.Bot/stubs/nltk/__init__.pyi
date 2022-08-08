# very very incomplete

import typing

T = typing.TypeVar("T")

def trigrams(
    sequence: typing.Sequence[T], **kwargs: typing.Any
) -> typing.Generator[tuple[T, ...], None, None]: ...
