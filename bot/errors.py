# define Python user-defined exceptions



class Error(Exception):
    """Base class for other exceptions"""
    pass


class ConfigAccessError(Error):
    """
    Exception raised for errors in the input.
    """

    def __init__(self,  message: str):
        self.message = message


class PrimaryKeyError(Error):
    """
    Raised if the primary key fails on insert
    """

    def __init__(self,  message: str):
        self.message = message
