import typing as t
from urllib.parse import urljoin

import discord
from discord.ext.commands._types import BotT
from discord.ext.commands.errors import BadArgument

from bot.bot_secrets import secrets
from bot.consts import Claims

if t.TYPE_CHECKING:
    from bot.clem_bot import ClemBot


def command(
    name: str | None = None, cls: t.Optional[type["ClemBotCommand"]] = None, **attrs: t.Any
) -> t.Callable[..., "ClemBotCommand"]:
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

    cls_ = cls or ClemBotCommand

    def wrapper(
        func: (
            ClemBotCommand
            | t.Callable[..., t.Any]
            | discord.ext.commands.Command[t.Any, t.Any, t.Any]
        ),
    ) -> ClemBotCommand:
        if isinstance(func, ClemBotCommand):
            raise TypeError("Callback is already a command.")

        return cls_(func, name=name, **attrs)

    return wrapper


"""
Decorator that enables the chaining of multiple commands
"""

T_EXTBASE: t.TypeAlias = t.Union[t.Any, "ExtBase"]
T_EXTBASE_DECO_WRAP: t.TypeAlias = t.Callable[[T_EXTBASE], T_EXTBASE]


def chainable(chainable: bool = True) -> T_EXTBASE_DECO_WRAP:
    def wrapper(func: "ExtBase" | t.Any) -> T_EXTBASE:
        if isinstance(func, ExtBase):
            func.chainable_output = chainable
        else:
            setattr(func, "chainable_output", chainable)

        return func

    return wrapper


def chainable_input(chainable: bool = True) -> T_EXTBASE_DECO_WRAP:
    def wrapper(func: "ExtBase" | t.Any) -> T_EXTBASE:
        if isinstance(func, ExtBase):
            func.chainable_output = chainable
        else:
            setattr(func, "chainable_input", chainable)

        return func

    return wrapper


"""
Helper decorators to allow for fluent style chain setting of Commmand attributes 
as opposed to setting them in the ctor
"""


def long_help(help_str: str) -> T_EXTBASE_DECO_WRAP:
    def wrapper(func: T_EXTBASE) -> T_EXTBASE:
        if isinstance(func, ExtBase):
            func.long_help = help_str
        else:
            setattr(func, "long_help", help_str)

        return func

    return wrapper


def short_help(help_str: str) -> T_EXTBASE_DECO_WRAP:
    def wrapper(func: T_EXTBASE) -> T_EXTBASE:
        if isinstance(func, ExtBase):
            func.short_help = help_str
        else:
            setattr(func, "short_help", help_str)

        return func

    return wrapper


def example(help_str: str | t.Iterable[str]) -> T_EXTBASE_DECO_WRAP:
    def wrapper(func: T_EXTBASE) -> T_EXTBASE:
        if isinstance(func, ExtBase):
            func.example = help_str
        else:
            setattr(func, "example", help_str)

        return func

    return wrapper


def ignore_claims_pre_invoke() -> T_EXTBASE_DECO_WRAP:
    """
    Tells the bot to not do a claim check before the command is invoked, allowing you to defer the check
    to inside the command
    """

    def wrapper(func: T_EXTBASE) -> T_EXTBASE:
        if isinstance(func, ExtBase):
            func.ignore_claims_pre_invoke = True
        else:
            setattr(func, "ignore_claims_pre_invoke", True)

        return func

    return wrapper


def required_claims(*claims: Claims) -> T_EXTBASE_DECO_WRAP:
    def wrapper(func: T_EXTBASE) -> T_EXTBASE:
        if any(not isinstance(c, Claims) for c in claims):
            raise BadArgument('All required claims must be of type <Enum "Claim">')

        set_claims = {c.name for c in claims}

        if isinstance(func, ExtBase):
            func.claims.update(set_claims)
        else:
            setattr(func, "claims", set_claims)

        return func

    return wrapper


def ban_disabling() -> T_EXTBASE_DECO_WRAP:
    def wrapper(func: T_EXTBASE) -> T_EXTBASE:
        if isinstance(func, ExtBase):
            func.allow_disable = False
        else:
            setattr(func, "allow_disable", False)

        return func

    return wrapper


def docs(page: str | list[str], header: str | None = None) -> T_EXTBASE_DECO_WRAP:
    def wrapper(func: T_EXTBASE) -> T_EXTBASE:
        if isinstance(func, ExtBase):
            func.page = page if isinstance(page, str) else "/".join(page)
            func.header = header
        else:
            setattr(func, "page", page if isinstance(page, str) else "/".join(page))
            setattr(func, "header", header)

        return func

    return wrapper


class ExtBase:
    def __init__(self, func: t.Any, **kwargs: t.Any) -> None:
        self.chainable_output = kwargs.get("chainable_output", False) or getattr(
            func, "chainable_output", False
        )
        self.chainable_input = kwargs.get("chainable_input", False) or getattr(
            func, "chainable_input", False
        )
        self.long_help: str = t.cast(
            str, kwargs.get("long_help") or getattr(func, "long_help", None)
        )
        self.short_help: str = t.cast(
            str, kwargs.get("short_help") or getattr(func, "short_help", None)
        )
        self.example: str | t.Iterable[str] = t.cast(
            str, kwargs.get("example") or getattr(func, "example", None)
        )
        self.claims: set[str] = kwargs.get("claims") or getattr(func, "claims", None) or set()
        self.ignore_claims_pre_invoke: bool = getattr(func, "ignore_claims_pre_invoke", False)
        self.allow_disable = t.cast(
            bool, kwargs.get("allow_disable") or getattr(func, "allow_disable", True)
        )
        self.page: str | None = getattr(func, "page", None)
        self.header: str | None = getattr(func, "header", None)

    def claims_check(self, claims: t.Sequence[str | Claims]) -> bool:
        """
        Checks if a given set of claims is valid for the current command

        Args:
            claims (list[str]): [description]

        Returns:
            bool: Authorization was successful
        """

        # check if there are any claims to check for if not authorize the command
        if len(self.claims) == 0:
            return True

        # Convert all values we got as Claims to their string name
        # so we can intersect them with the commands internal auth values
        str_claims: list[str] = []
        for c in claims:
            if isinstance(c, Claims):
                str_claims.append(c.name)
            else:
                str_claims.append(c)

        # check for intersection of two sets of claims, if there is one we have a valid user
        return len(set(str_claims).intersection(self.claims)) > 0

    def docs_url(self) -> str | None:
        """
        Gets the full URL of the documentation for the command.
        Uses the `docs_url` string stored in BotSecrets and appends the page and header, if given.

        Returns:
            The full URL to the documentation of the command or None if `BotSecrets.docs_url` is None or `page` is None.
        """
        if not secrets.docs_url or not self.page:
            return None

        return f"{urljoin(secrets.docs_url, self.page)}{f'#{self.header}' if self.header else ''}"


class ClemBotCommand(discord.ext.commands.Command[t.Any, t.Any, t.Any], ExtBase):
    def __init__(self, func: t.Callable[..., t.Coroutine[None, None, t.Any]], **kwargs: t.Any):
        discord.ext.commands.Command.__init__(self, func, **kwargs)

        ExtBase.__init__(self, func, **kwargs)

    def command(self, *args: t.Any, **kwargs: t.Any) -> t.Callable[..., "ClemBotCommand"]:
        """
        A shortcut decorator that invokes :func:`.command` and adds it to
        the internal command list via :meth:`~.GroupMixin.add_command`.
        Returns
        --------
        Callable[..., :class:`Command`]
            A decorator that converts the provided method into a Command, adds it to the bot, then returns it.
        """

        def decorator(func: t.Any) -> ClemBotCommand:
            kwargs.setdefault("parent", self)
            result: ClemBotCommand = super.command(*args, **kwargs)(func)  # type: ignore
            super.add_command(result)  # type: ignore
            return result

        return decorator


def group(name: t.Optional[str] = None, **attrs: t.Any) -> t.Callable[..., "ClemBotGroup"]:
    """A decorator that transforms a function into a :class:`.Group`.
    This is similar to the :func:`.command` decorator but the ``cls``
    parameter is set to :class:`Group` by default.
    .. versionchanged:: 1.1
        The ``cls`` parameter can now be passed.
    """

    attrs.setdefault("cls", ClemBotGroup)
    return t.cast(t.Callable[..., ClemBotGroup], command(name=name, **attrs))


class ClemBotGroup(discord.ext.commands.Group[t.Any, t.Any, t.Any], ExtBase):
    def __init__(
        self, func: t.Callable[..., t.Coroutine[None, None, t.Any]], **kwargs: t.Any
    ) -> None:
        discord.ext.commands.Group.__init__(self, func, **kwargs)
        ExtBase.__init__(self, func, **kwargs)

    def command(self, *args: t.Any, **kwargs: t.Any) -> t.Callable[..., ClemBotCommand]:  # type: ignore
        """A shortcut decorator that invokes :func:`.command` and adds it to
        the internal command list via :meth:`~.GroupMixin.add_command`.
        Returns
        --------
        Callable[..., :class:`Command`]
            A decorator that converts the provided method into a Command, adds it to the bot, then returns it.
        """

        def decorator(func: t.Any) -> ClemBotCommand:
            kwargs.setdefault("parent", self)
            result = command(*args, **kwargs)(func)
            self.add_command(result)
            return result

        return decorator

    def group(self, name=None, **attrs) -> t.Callable[..., "ClemBotGroup"]:  # type: ignore
        """A shortcut decorator that invokes :func:`.command` and adds it to
        the internal command list via :meth:`~.GroupMixin.add_command`.
        Returns
        --------
        Callable[..., :class:`Command`]
            A decorator that converts the provided method into a Command, adds it to the bot, then returns it.
        """
        attrs.setdefault("cls", ClemBotGroup)
        return t.cast(t.Callable[..., ClemBotGroup], self.command(name=name, **attrs))


class ClemBotContext(discord.ext.commands.Context[BotT]):
    command: ClemBotCommand | None
    guild: discord.Guild
    author: discord.Member


ClemBotCtx: t.TypeAlias = ClemBotContext["ClemBot"]
