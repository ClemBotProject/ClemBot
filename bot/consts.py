from enum import Enum, auto

class Colors:
    """Hex Color values"""

    Error = 0xE20000
    ClemsonOrange = 0xF56600

class DesignatedChannelBase(Enum):
    pass

class DesignatedChannels(DesignatedChannelBase):
    """Enum that defines possible designated channels for the bot to use"""

    message_log = auto()
    moderation_log = auto()
    error_log = auto()
    startup_log = auto()
    user_join_log = auto()
    starboard = auto()

    @staticmethod
    def has(member: str) -> bool:
        return member in DesignatedChannels.__members__
class OwnerDesignatedChannels(DesignatedChannelBase):

    server_join_log = auto()

    @staticmethod
    def has(member: str) -> bool:
        return member in OwnerDesignatedChannels.__members__

class DiscordLimits:
    MessageLength = 1900
    EmbedFieldLength = 900
