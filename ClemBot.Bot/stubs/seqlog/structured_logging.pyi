import logging
from types import TracebackType
import typing as tp
from .consumer import QueueConsumer as QueueConsumer
from _typeshed import Incomplete

_SysExcInfoType: tp.TypeAlias = tp.Union[tuple[type[BaseException], BaseException, TracebackType | None], tuple[None, None, None]]
_ExcInfoType: tp.TypeAlias = None | bool | _SysExcInfoType | BaseException

def get_global_log_properties(logger_name: Incomplete | None = ...) -> tp.Any: ...
def set_global_log_properties(**properties: tp.Any) -> None: ...
def reset_global_log_properties() -> None: ...
def clear_global_log_properties() -> None: ...
def set_callback_on_failure(callback: tp.Callable[[Exception], None]) -> None: ...

class StructuredLogRecord(logging.LogRecord):
    log_props: Incomplete
    def __init__(self, name: tp.Any, level: tp.Any, pathname: tp.Any, lineno: tp.Any, msg: tp.Any, args: tp.Any, exc_info: tp.Any, func: Incomplete | None = ..., sinfo: Incomplete | None = ..., log_props: Incomplete | None = ..., **kwargs: tp.Any) -> None: ...
    def getMessage(self) -> tp.Any: ...

class StructuredLogger(logging.Logger):
    def __init__(self, name: tp.Any, level: tp.Any = ...) -> None: ...
    def makeRecord(self, name: tp.Any, level: tp.Any, fn: tp.Any, lno: tp.Any, msg: tp.Any, args: tp.Any, exc_info: tp.Any, func: Incomplete | None = ..., extra: Incomplete | None = ..., sinfo: Incomplete | None = ...) -> tp.Any: ...
    def debug(
        self,
        msg: object,
        *args: object,
        exc_info: _ExcInfoType = ...,
        stack_info: bool = ...,
        stacklevel: int = ...,
        extra: tp.Mapping[str, object] | None = ...,
        **kwargs: tp.Any,
    ) -> None: ...
    def info(
        self,
        msg: object,
        *args: object,
        exc_info: _ExcInfoType = ...,
        stack_info: bool = ...,
        stacklevel: int = ...,
        extra: tp.Mapping[str, object] | None = ...,
        **kwargs: tp.Any,
    ) -> None: ...
    def warning(
        self,
        msg: object,
        *args: object,
        exc_info: _ExcInfoType = ...,
        stack_info: bool = ...,
        stacklevel: int = ...,
        extra: tp.Mapping[str, object] | None = ...,
        **kwargs: tp.Any,
    ) -> None: ...
    def warn(
        self,
        msg: object,
        *args: object,
        exc_info: _ExcInfoType = ...,
        stack_info: bool = ...,
        stacklevel: int = ...,
        extra: tp.Mapping[str, object] | None = ...,
        **kwargs: tp.Any,
    ) -> None: ...
    def error(
        self,
        msg: object,
        *args: object,
        exc_info: _ExcInfoType = ...,
        stack_info: bool = ...,
        stacklevel: int = ...,
        extra: tp.Mapping[str, object] | None = ...,
        **kwargs: tp.Any,
    ) -> None: ...
    def exception(
        self,
        msg: object,
        *args: object,
        exc_info: _ExcInfoType = ...,
        stack_info: bool = ...,
        stacklevel: int = ...,
        extra: tp.Mapping[str, object] | None = ...,
        **kwargs: tp.Any,
    ) -> None: ...
    def critical(
        self,
        msg: object,
        *args: object,
        exc_info: _ExcInfoType = ...,
        stack_info: bool = ...,
        stacklevel: int = ...,
        extra: tp.Mapping[str, object] | None = ...,
        **kwargs: tp.Any,
    ) -> None: ...

class StructuredRootLogger(logging.RootLogger):
    def __init__(self, level: tp.Any = ...) -> None: ...
    def makeRecord(self, name: tp.Any, level: tp.Any, fn: tp.Any, lno: tp.Any, msg: tp.Any, args: tp.Any, exc_info: tp.Any, func: Incomplete | None = ..., extra: Incomplete | None = ..., sinfo: Incomplete | None = ...) -> tp.Any: ...

class ConsoleStructuredLogHandler(logging.Handler):
    def __init__(self) -> None: ...
    def emit(self, record: tp.Any) -> None: ...

class SeqLogHandler(logging.Handler):
    server_url: Incomplete
    session: Incomplete
    json_encoder_class: Incomplete
    log_queue: Incomplete
    consumer: Incomplete
    def __init__(self, server_url: tp.Any, api_key: Incomplete | None = ..., batch_size: int = ..., auto_flush_timeout: Incomplete | None = ..., json_encoder_class: Incomplete | None = ...) -> None: ...
    def flush(self) -> None: ...
    def emit(self, record: tp.Any) -> None: ...
    def close(self) -> None: ...
    def publish_log_batch(self, batch: tp.Iterable[StructuredLogRecord]) -> None: ...

