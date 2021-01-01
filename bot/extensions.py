import dataclasses
import discord.ext.commands


def command(name=None, cls=None, **attrs):
    """
    -----------
    name: :class:`str`
        The name to create the command with. By default this uses the
        function name unchanged.
    cls
        The class to construct with. By default this is :class:`.Command`.
        You usually do not change this.
    attrs
        Keyword arguments to pass into the construction of the class denoted
        by ``cls``.
    Raises
    -------
    TypeError
        If the function is not a coroutine or is already a command.
    """
    if cls is None:
        cls = ClemBotCommand

    def wrapper(func):
        if isinstance(func, ClemBotCommand):
            raise TypeError('Callback is already a command.')
        return cls(func, name=name, **attrs)

    return wrapper

"""
Helper decorators to allow for fluent style chain setting of Commmand attributes 
as opposed to setting them in the ctor
"""
def long_help(help_str: str):
    def wrapper(func):
        if isinstance(func, HelpAttrs):
            func.long_help = help_str
        else:
            setattr(func, 'long_help', help_str)
        return func
    return wrapper

def short_help(help_str: str):
    def wrapper(func):
        if isinstance(func, HelpAttrs):
            func.short_help = help_str
        else:
            setattr(func, 'short_help', help_str)
        return func
    return wrapper

def example(help_str: str):
    def wrapper(func):
        if isinstance(func, HelpAttrs):
            func.example = help_str
        else:
            setattr(func, 'example', help_str)
        return func
    return wrapper


@dataclasses.dataclass(frozen=True)
class HelpAttrs:
    long_help: str
    short_help: str
    example: str

class ClemBotCommand(discord.ext.commands.Command, HelpAttrs):

    def __init__(self, func, *, 
                long_help: str=None, 
                short_help: str=None,
                example: str=None, 
                **kwargs) -> None:

        discord.ext.commands.Command.__init__(self, func, **kwargs)

        long_help = long_help or getattr(func, 'long_help', None)
        short_help = short_help or getattr(func, 'short_help', None)
        example = example or getattr(func, 'example', None)

        HelpAttrs.__init__(self, long_help=long_help, short_help=short_help, example=example)

    def command(self, *args, **kwargs):
        """
        A shortcut decorator that invokes :func:`.command` and adds it to
        the internal command list via :meth:`~.GroupMixin.add_command`.
        Returns
        --------
        Callable[..., :class:`Command`]
            A decorator that converts the provided method into a Command, adds it to the bot, then returns it.
        """
        def decorator(func):
            kwargs.setdefault('parent', self)
            result = super.command(*args, **kwargs)(func)
            super.add_command(result)
            return result

        return decorator

def group(name=None, **attrs):
    """A decorator that transforms a function into a :class:`.Group`.
    This is similar to the :func:`.command` decorator but the ``cls``
    parameter is set to :class:`Group` by default.
    .. versionchanged:: 1.1
        The ``cls`` parameter can now be passed.
    """

    attrs.setdefault('cls', ClemBotGroup)
    return command(name=name, **attrs)

class ClemBotGroup(discord.ext.commands.Group, HelpAttrs):

    def __init__(self, func, *, 
                long_help: str=None, 
                short_help: str=None,
                example: str=None, 
                **kwargs) -> None:

        discord.ext.commands.Group.__init__(self, func, **kwargs)

        long_help = long_help or getattr(func, 'long_help', None)
        short_help = short_help or getattr(func, 'short_help', None)
        example = example or getattr(func, 'example', None)

        HelpAttrs.__init__(self, long_help=long_help, short_help=short_help, example=example)


    def command(self, *args, **kwargs):
        """A shortcut decorator that invokes :func:`.command` and adds it to
        the internal command list via :meth:`~.GroupMixin.add_command`.
        Returns
        --------
        Callable[..., :class:`Command`]
            A decorator that converts the provided method into a Command, adds it to the bot, then returns it.
        """
        def decorator(func):
            kwargs.setdefault('parent', self)
            result = command(*args, **kwargs)(func)
            self.add_command(result)
            return result

        return decorator