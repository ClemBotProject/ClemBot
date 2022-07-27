import logging
import typing as t

import seqlog


def get_logger(name: str) -> seqlog.StructuredLogger:
    """Provides a way to get seqlog StructuredLogger instance without mypy being angry"""

    return t.cast(seqlog.StructuredLogger, logging.getLogger(name))
