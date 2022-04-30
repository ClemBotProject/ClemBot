# define Python user-defined exceptions
from discord.ext.commands import CommandError


class ConfigAccessError(Exception):
    """
    Exception raised for errors in the input.
    """

    def __init__(self, message: str):
        self.message = message


class PrimaryKeyError(Exception):
    """
    Raised if the primary key fails on insert
    """

    def __init__(self, message: str):
        self.message = message


class DesignatedChannelError(Exception):
    """
    Raised if a channel is set to a designated channel type the doesnt exist
    """

    def __init__(self, message: str):
        self.message = message


class ParserError(Exception):
    """
    Raised if user inputs bad data
    """

    def __init__(self, message: str):
        self.message = message


class ClaimsAccessError(CommandError):
    """
    Raised if a user attempts to use a command that they do not have claims for
    """

    def __init__(self, message: str):
        self.message = message


class ConversionError(CommandError):

    def __init__(self, message):
        self.message = message


class ApiClientRequestError(Exception):

    def __init__(self, message):
        self.message = message


class BotOnlyRequestError(Exception):

    def __init__(self, message):
        self.message = message


class PrefixRequestError(Exception):

    def __init__(self, message):
        self.message = message