"""
This module is to define all application level events in one place 
to avoid attempting to remember string event names
"""

class Events:
    """Class that defines what events are exposed at the bot level"""

    on_message_recieved = 'on_message_recieved'
    """
    Published whenever a message is sent in a server
    
    Args:
        message (Message) – The deleted message.
    """

    on_message_edit = 'on_message_edit'
    """
    Published when a Message receives an update event and is in the cache

    Args:
        before (Message) – The previous version of the message.
        after (Message) – The current version of the message.
    """

    on_message_delete = 'on_message_delete'
    """
    Published whenever a message is deleted while it exists in the cache

    Args:
        message (Message) – The message that was deleted
    """

    on_reaction_add = 'on_reaction_add'
    """"
    Published whenever a reaction is sent in a server, and that message is stored
    in d.pys internal cache

    Args:
        reaction (Reaction) – The current state of the reaction.
        user (Union[Member, User]) – The user who added the reaction.
    """

    on_raw_reaction_add = 'on_raw_reaction_add'
    """
    Called when a message has a reaction added. regardless of cache state

    Args:
        payload (RawReactionActionEvent) – The raw event payload data.
    """

    on_reaction_remove = 'on_reaction_remove'
    """"
    Published whenever a reaction is removed in a server, and that message is stored
    in d.pys internal cache

    Args:
        reaction (Reaction) – The current state of the reaction.
        user (Union[Member, User]) – The user who removeed the reaction.
    """

    on_raw_reaction_remove = 'on_raw_reaction_remove'
    """
    Called when a message has a reaction removeed. regardless of cache state

    Args:
        payload (RawReactionActionEvent) – The raw event payload data.
    """

    on_guild_joined = 'on_guild_joined'
    """"
    Published whenever the bot joins new guild

    Args:
        guild (Guild) – The guild that was joined.    
    """

    on_guild_role_create = 'on_guild_role_create'
    """"
    published whenever a guild role is created in a guild
    
    Args:
        role (Role) – The role that was created or deleted.
    """

    on_guild_role_update = 'on_guild_role_update'
    """"
    published whenever a guild role is updated in a guild
    
    Args:
        before (Role) – The updated role’s old info.
        after (Role) – The updated role’s updated info.
    """

    on_guild_role_delete = 'on_guild_role_delete'
    """"
    published whenever a guild role is deleted in a guild
    
    Args:
        role (Role) – The role that was created or deleted.
    """

    on_user_joined = 'on_user_joined'
    """"
    Published whenever a new user joins a guild
    
    Args:
        user (User) – The user who joined or left.
    """

    on_user_left = 'on_user_left'
    """"
    Published whenever a user leaves a guild
    
    Args:
        user (User) – The user who joined or left.
    """

    on_user_update = 'on_user_update'
    """"
    Published whenever a user updates themselves
    
    Args:
        before (User) – The updated user’s old info. 
        after (User) – The updated user’s updated info.
    """

    on_add_designated_channel = 'on_add_designated_channel'
    """
    Published whenever a designated channel id is added to a designated channel slot

    Args:
        channel (Channel) the channel object that was added
    """

    on_send_in_designated_channel = 'on_send_in_designated_channel'
    """
    Published when a reqeust to send a message in a designated channel is sent

    Args:
        channel_type (str) The designated channel to send the message in
        message (union[embed, str]) the message to be sent to the channel
    """