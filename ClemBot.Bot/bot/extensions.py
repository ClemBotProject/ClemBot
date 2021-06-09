import typing as t

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
Decorator that enables the chaining of multiple commands
"""


def chainable(chainable: bool = True):
    def wrapper(func):
        if isinstance(func, ExtBase):
            func.chainable_output = chainable
        else:
            setattr(func, 'chainable_output', chainable)
        return func
    return wrapper


def chainable_input(chainable: bool = True):
    def wrapper(func):
        if isinstance(func, ExtBase):
            func.chainable_output = chainable
        else:
            setattr(func, 'chainable_input', chainable)
        return func
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


def example(help_str: t.Union[str, t.Iterable[str]]):
    def wrapper(func):
        if isinstance(func, ExtBase):
            func.example = help_str
        else:
            setattr(func, 'example', help_str)
        return func
    return wrapper


def ignore_claims_pre_invoke():
    """
    Tells the bot to not do a claim check before the command is invoked, allowing you to defer the check 
    to inside the command
    """

    def wrapper(func):
        if isinstance(func, ExtBase):
            func.ignore_claims_pre_invoke = True
        else:
            setattr(func, 'ignore_claims_pre_invoke', True)
        return func
    return wrapper


def required_claims(*claims):
    def wrapper(func):
        if any(not isinstance(c, Claims) for c in claims):
            raise BadArgument('All required claims must be of type <Enum "Claim">')
        set_claims = set(c.name for c in claims)
        if isinstance(func, ExtBase):
            func.claims.update(set_claims)
        else:
            setattr(func, 'claims', set_claims)
        return func
    return wrapper


class ExtBase:
    def __init__(self, func, **kwargs) -> None:
        self.chainable_output = kwargs.get('chainable_output', False) or getattr(func, 'chainable_output', False)
        self.chainable_input = kwargs.get('chainable_input', False) or getattr(func, 'chainable_input', False)
        self.long_help = kwargs.get('long_help') or getattr(func, 'long_help', None)
        self.short_help = kwargs.get('short_help') or getattr(func, 'short_help', None)
        self.example = kwargs.get('example') or getattr(func, 'example', None)
        self.claims = kwargs.get('claims') or getattr(func, 'claims', set())
        self.ignore_claims_pre_invoke = getattr(func, 'ignore_claims_pre_invoke', False)

    def claims_check(self, claims: t.List[Claims]) -> bool:
        """
        Checks if a given set of claims is valid for the current command

        Args:
            claims (t.List[str]): [description]

        Returns:
            bool: Authorization was successful
        """

        # check if there are any claims to check for if not authorize the command
        if len(self.claims) == 0:
            return True

        # check for intersection of two sets of claims, if there is one we have a valid user
        return len(set(claims).intersection(self.claims)) > 0


class ClemBotCommand(discord.ext.commands.Command, ExtBase):

    def __init__(self, func, **kwargs) -> None:
        discord.ext.commands.Command.__init__(self, func, **kwargs)

        ExtBase.__init__(self, func, **kwargs)

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

    def __init__(self, func, **kwargs) -> None:
        discord.ext.commands.Group.__init__(self, func, **kwargs)
        ExtBase.__init__(self, func, **kwargs)

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
