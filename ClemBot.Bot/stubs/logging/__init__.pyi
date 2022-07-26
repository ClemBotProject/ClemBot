from _typeshed import Incomplete

raiseExceptions: bool
CRITICAL: int
FATAL = CRITICAL
ERROR: int
WARNING: int
WARN = WARNING
INFO: int
DEBUG: int
NOTSET: int

def getLevelName(level): ...
def addLevelName(level, levelName) -> None: ...

class LogRecord:
    name: Incomplete
    msg: Incomplete
    args: Incomplete
    levelname: Incomplete
    levelno: Incomplete
    pathname: Incomplete
    filename: Incomplete
    module: Incomplete
    exc_info: Incomplete
    exc_text: Incomplete
    stack_info: Incomplete
    lineno: Incomplete
    funcName: Incomplete
    created: Incomplete
    msecs: Incomplete
    relativeCreated: Incomplete
    thread: Incomplete
    threadName: Incomplete
    processName: Incomplete
    process: Incomplete
    def __init__(self, name, level, pathname, lineno, msg, args, exc_info, func: Incomplete | None = ..., sinfo: Incomplete | None = ..., **kwargs) -> None: ...
    def getMessage(self): ...

def setLogRecordFactory(factory) -> None: ...
def getLogRecordFactory(): ...
def makeLogRecord(dict): ...

class PercentStyle:
    default_format: str
    asctime_format: str
    asctime_search: str
    validation_pattern: Incomplete
    def __init__(self, fmt, *, defaults: Incomplete | None = ...) -> None: ...
    def usesTime(self): ...
    def validate(self) -> None: ...
    def format(self, record): ...

class StrFormatStyle(PercentStyle):
    default_format: str
    asctime_format: str
    asctime_search: str
    fmt_spec: Incomplete
    field_spec: Incomplete
    def validate(self) -> None: ...

class StringTemplateStyle(PercentStyle):
    default_format: str
    asctime_format: str
    asctime_search: str
    def __init__(self, *args, **kwargs) -> None: ...
    def usesTime(self): ...
    def validate(self) -> None: ...

BASIC_FORMAT: str

class Formatter:
    converter: Incomplete
    datefmt: Incomplete
    def __init__(self, fmt: Incomplete | None = ..., datefmt: Incomplete | None = ..., style: str = ..., validate: bool = ..., *, defaults: Incomplete | None = ...) -> None: ...
    default_time_format: str
    default_msec_format: str
    def formatTime(self, record, datefmt: Incomplete | None = ...): ...
    def formatException(self, ei): ...
    def usesTime(self): ...
    def formatMessage(self, record): ...
    def formatStack(self, stack_info): ...
    def format(self, record): ...

class BufferingFormatter:
    linefmt: Incomplete
    def __init__(self, linefmt: Incomplete | None = ...) -> None: ...
    def formatHeader(self, records): ...
    def formatFooter(self, records): ...
    def format(self, records): ...

class Filter:
    name: Incomplete
    nlen: Incomplete
    def __init__(self, name: str = ...) -> None: ...
    def filter(self, record): ...

class Filterer:
    filters: Incomplete
    def __init__(self) -> None: ...
    def addFilter(self, filter) -> None: ...
    def removeFilter(self, filter) -> None: ...
    def filter(self, record): ...

class Handler(Filterer):
    level: Incomplete
    formatter: Incomplete
    def __init__(self, level=...) -> None: ...
    def get_name(self): ...
    def set_name(self, name) -> None: ...
    name: Incomplete
    lock: Incomplete
    def createLock(self) -> None: ...
    def acquire(self) -> None: ...
    def release(self) -> None: ...
    def setLevel(self, level) -> None: ...
    def format(self, record): ...
    def emit(self, record) -> None: ...
    def handle(self, record): ...
    def setFormatter(self, fmt) -> None: ...
    def flush(self) -> None: ...
    def close(self) -> None: ...
    def handleError(self, record) -> None: ...

class StreamHandler(Handler):
    terminator: str
    stream: Incomplete
    def __init__(self, stream: Incomplete | None = ...) -> None: ...
    def flush(self) -> None: ...
    def emit(self, record) -> None: ...
    def setStream(self, stream): ...

class FileHandler(StreamHandler):
    baseFilename: Incomplete
    mode: Incomplete
    encoding: Incomplete
    errors: Incomplete
    delay: Incomplete
    stream: Incomplete
    def __init__(self, filename, mode: str = ..., encoding: Incomplete | None = ..., delay: bool = ..., errors: Incomplete | None = ...) -> None: ...
    def close(self) -> None: ...
    def emit(self, record) -> None: ...

class _StderrHandler(StreamHandler):
    def __init__(self, level=...) -> None: ...
    @property
    def stream(self): ...

lastResort: Incomplete

class PlaceHolder:
    loggerMap: Incomplete
    def __init__(self, alogger) -> None: ...
    def append(self, alogger) -> None: ...

def setLoggerClass(klass) -> None: ...
def getLoggerClass(): ...

class Manager:
    root: Incomplete
    emittedNoHandlerWarning: bool
    loggerDict: Incomplete
    loggerClass: Incomplete
    logRecordFactory: Incomplete
    def __init__(self, rootnode) -> None: ...
    @property
    def disable(self): ...
    @disable.setter
    def disable(self, value) -> None: ...
    def getLogger(self, name): ...
    def setLoggerClass(self, klass) -> None: ...
    def setLogRecordFactory(self, factory) -> None: ...

class Logger(Filterer):
    name: Incomplete
    level: Incomplete
    parent: Incomplete
    propagate: bool
    handlers: Incomplete
    disabled: bool
    def __init__(self, name, level=...) -> None: ...
    def setLevel(self, level) -> None: ...
    def debug(self, msg, *args, **kwargs) -> None: ...
    def info(self, msg, *args, **kwargs) -> None: ...
    def warning(self, msg, *args, **kwargs) -> None: ...
    def warn(self, msg, *args, **kwargs) -> None: ...
    def error(self, msg, *args, **kwargs) -> None: ...
    def exception(self, msg, *args, exc_info: bool = ..., **kwargs) -> None: ...
    def critical(self, msg, *args, **kwargs) -> None: ...
    def fatal(self, msg, *args, **kwargs) -> None: ...
    def log(self, level, msg, *args, **kwargs) -> None: ...
    def findCaller(self, stack_info: bool = ..., stacklevel: int = ...): ...
    def makeRecord(self, name, level, fn, lno, msg, args, exc_info, func: Incomplete | None = ..., extra: Incomplete | None = ..., sinfo: Incomplete | None = ...): ...
    def handle(self, record) -> None: ...
    def addHandler(self, hdlr) -> None: ...
    def removeHandler(self, hdlr) -> None: ...
    def hasHandlers(self): ...
    def callHandlers(self, record) -> None: ...
    def getEffectiveLevel(self): ...
    def isEnabledFor(self, level): ...
    def getChild(self, suffix): ...
    def __reduce__(self): ...

class RootLogger(Logger):
    def __init__(self, level) -> None: ...
    def __reduce__(self): ...

class LoggerAdapter:
    logger: Incomplete
    extra: Incomplete
    def __init__(self, logger, extra: Incomplete | None = ...) -> None: ...
    def process(self, msg, kwargs): ...
    def debug(self, msg, *args, **kwargs) -> None: ...
    def info(self, msg, *args, **kwargs) -> None: ...
    def warning(self, msg, *args, **kwargs) -> None: ...
    def warn(self, msg, *args, **kwargs) -> None: ...
    def error(self, msg, *args, **kwargs) -> None: ...
    def exception(self, msg, *args, exc_info: bool = ..., **kwargs) -> None: ...
    def critical(self, msg, *args, **kwargs) -> None: ...
    def log(self, level, msg, *args, **kwargs) -> None: ...
    def isEnabledFor(self, level): ...
    def setLevel(self, level) -> None: ...
    def getEffectiveLevel(self): ...
    def hasHandlers(self): ...
    @property
    def manager(self): ...
    @manager.setter
    def manager(self, value) -> None: ...
    @property
    def name(self): ...

def basicConfig(**kwargs) -> None: ...
def getLogger(name: Incomplete | None = ...): ...
def critical(msg, *args, **kwargs) -> None: ...
def fatal(msg, *args, **kwargs) -> None: ...
def error(msg, *args, **kwargs) -> None: ...
def exception(msg, *args, exc_info: bool = ..., **kwargs) -> None: ...
def warning(msg, *args, **kwargs) -> None: ...
def warn(msg, *args, **kwargs) -> None: ...
def info(msg, *args, **kwargs) -> None: ...
def debug(msg, *args, **kwargs) -> None: ...
def log(level, msg, *args, **kwargs) -> None: ...
def disable(level=...) -> None: ...
def shutdown(handlerList=...) -> None: ...

class NullHandler(Handler):
    def handle(self, record) -> None: ...
    def emit(self, record) -> None: ...
    lock: Incomplete
    def createLock(self) -> None: ...

def captureWarnings(capture) -> None: ...
