import typing as t
from collections.abc import Iterable

import discord.ext.commands
from discord.ext.commands.errors import BadArgument

from bot.consts import Claims


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
        if isinstance(func, ExtBase):
            func.long_help = help_str
        else:
            setattr(func, 'long_help', help_str)
        return func
    return wrapper

def short_help(help_str: str):
    def wrapper(func):
        if isinstance(func, ExtBase):
            func.short_help = help_str
        else:
            setattr(func, 'short_help', help_str)
        return func
    return wrapper

def example(help_str: str):
    def wrapper(func):
        if isinstance(func, ExtBase):
            func.example = help_str
        else:
            setattr(func, 'example', help_str)
        return func
    return wrapper

def required_claims(*claims):
    def wrapper(func):
        if any(not isinstance(c, Claims) for c in claims):
            raise BadArgument('All required claims must be of type <Enum "Claim">')
        set_claims = set(claims)
        if isinstance(func, ExtBase):
            func.claims.update(set_claims)
        else:
            setattr(func, 'claims', set_claims)
        return func
    return wrapper


class ExtBase:
    def __init__(self, **kwargs) -> None:

        self.long_help = kwargs.get('long_help', None)
        self.short_help = kwargs.get('short_help', None)
        self.example = kwargs.get('example', None)
        self.claims = kwargs.get('claims', None) or set()

    def claims_check(self, claims: t.List[Claims]) -> bool:
        """
        Checks if a given set of claims is valid for the current command

        Args:
            claims (t.List[str]): [description]

        Returns:
            bool: Authorization was successful
        """

        #check if there are any claims to check for if not authorize the command
        if len(self.claims) == 0:
            return True

        #check for intersection of two sets of claims, if there is one we have a valid user
        return len(set(claims).intersection(self.claims)) > 0

class ClemBotCommand(discord.ext.commands.Command, ExtBase):

    def __init__(self, func, *, 
                long_help: str=None, 
                short_help: str=None,
                example: str=None, 
                **kwargs) -> None:

        discord.ext.commands.Command.__init__(self, func, **kwargs)

        long_help = long_help or getattr(func, 'long_help', None)
        short_help = short_help or getattr(func, 'short_help', None)
        example = example or getattr(func, 'example', None)
        claims = kwargs.get('claims', None) or getattr(func, 'claims', None)

        ExtBase.__init__(self, long_help=long_help, short_help=short_help, example=example, claims=claims)

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

class ClemBotGroup(discord.ext.commands.Group, ExtBase):

    def __init__(self, func, *, 
                long_help: str=None, 
                short_help: str=None,
                example: str=None, 
                **kwargs) -> None:

        discord.ext.commands.Group.__init__(self, func, **kwargs)

        long_help = long_help or getattr(func, 'long_help', None)
        short_help = short_help or getattr(func, 'short_help', None)
        example = example or getattr(func, 'example', None)

        ExtBase.__init__(self, long_help=long_help, short_help=short_help, example=example)


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