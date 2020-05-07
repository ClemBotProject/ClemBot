# define Python user-defined exceptions


class Error(Exception):
    """Base class for other exceptions"""
    pass


class ConfigAccessError(Error):
    """Exception raised for errors in the input.

    Attributes:
        message -- explanation of the error
    """

    def __init__(self,  message: str):
        self.message = message


class PrimaryKeyError(Error):
    """Raised if the primary key fails on insert

    Attributes:
        message -- explanation of the error
    """

    def __init__(self,  message: str):
        self.message = message
