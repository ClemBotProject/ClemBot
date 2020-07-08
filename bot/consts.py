from enum import Enum, auto

class Colors:
    """Hex Color values"""

    Error = 0xE20000
    ClemsonOrange = 0xF56600

class DesignatedChannels(Enum):
    """Enum that defines possible designated channels for the bot to use"""

    message_log = auto()
    moderation_log = auto()
    error_log = auto()
    startup_log = auto()
