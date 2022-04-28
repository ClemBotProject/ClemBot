from enum import Enum, auto


class Urls:
    base_api_url = 'api/'


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
    user_join_log = auto()
    user_leave_log = auto()
    starboard = auto()

    @staticmethod
    def has(member: str) -> bool:
        return member in DesignatedChannels.__members__


class OwnerDesignatedChannels(DesignatedChannelBase):
    server_join_log = auto()
    bot_dm_log = auto()

    @staticmethod
    def has(member: str) -> bool:
        return member in OwnerDesignatedChannels.__members__


class GuildSettings(Enum):
    allow_embed_links = auto()


class Claims(Enum):
    """Represents all possible authorization claims that server roles can have"""

    designated_channel_view = auto()
    designated_channel_modify = auto()
    custom_prefix_set = auto()
    welcome_message_view = auto()
    welcome_message_modify = auto()
    tag_add = auto()
    tag_delete = auto()
    assignable_roles_add = auto()
    assignable_roles_delete = auto()
    delete_message = auto()
    emote_add = auto()
    claims_view = auto()
    claims_modify = auto()
    manage_class_add = auto()
    moderation_warn = auto()
    moderation_ban = auto()
    moderation_mute = auto()
    moderation_purge = auto()
    moderation_infraction_view = auto()
    moderation_infraction_view_self = auto()
    dashboard_view = auto()
    dashboard_edit = auto()
    guild_settings_view = auto()
    guild_settings_edit = auto()
    custom_tag_prefix_set = auto()

    @staticmethod
    def get_claims_str():
        return '\n'.join(name for name, _ in Claims.__members__.items())


class DiscordLimits:
    MessageLength = 1900
    EmbedFieldLength = 900


class Infractions:
    mute = 'Mute'
    ban = 'Ban'
    warn = 'Warn'


class Moderation:
    mute_role_name = 'ClemBot Mute'
