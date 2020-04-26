import logging

from bot.exceptions.error import Error
log = logging.getLogger(__name__)


class ConfigAccessError(Error):
    """Exception raised for errors in the input.

    Attributes:
        expression -- input expression in which the error occurred
        message -- explanation of the error
    """

    def __init__(self,  message: str):
        self.message = message
