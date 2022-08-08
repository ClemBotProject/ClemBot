import abc
import inspect
import typing as t

from bot.clem_bot import ClemBot


class BaseService(abc.ABC):
    """
    This is the base service class that all services must inherit from
    The bot reflects over itself at runtime and loads all instances with
    this class as a base class
    """

    def __init__(self, bot: ClemBot) -> None:
        self.bot: ClemBot = bot
        self.messenger = bot.messenger

        for _, value in inspect.getmembers(self):
            event = None
            if hasattr(value, "__event_listener__"):
                event = getattr(value, "__event_listener__")
            if event:
                self.bot.messenger.subscribe(event, value)

    @abc.abstractmethod
    async def load_service(self) -> None:
        """
        The abstract base method to enforce that all child services must
        implement a load_service method to handle on startup tasks
        """
        pass

    @classmethod
    def listener(cls, event: str | None = None) -> t.Callable[[t.Any], t.Any]:
        """
        The method decorator to allow for service methods to be marked as a callback
        for application level events

        Args:
            event ([Str], optional): The event that the method is subscribing too.
            Defaults to None.
        """

        def wrapper(func: t.Any) -> t.Any:
            actual = func
            if isinstance(actual, staticmethod):
                actual = actual.__func__
            if not inspect.iscoroutinefunction(actual):
                raise TypeError("Listener function must be a coroutine function.")
            actual.__event_listener__ = event or actual.__name__

            return func

        return wrapper
