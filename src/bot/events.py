"""
This module is to define all application level events in one place 
to avoid attempting to remember string event names
"""

class Events:
    """Published whenever a message is sent in a server"""
    on_message_recieved = 'on_message_recieved'

    """Published whenever a reaction is sent in a server"""
    on_reaction_recieved = 'on_reaction_recieved'

    """Published whenever the bot joins new guild"""
    on_guild_joined = 'on_guild_joined'

    """Published whenever a new user joins a guild"""
    on_user_joined = 'on_user_joined'

    """Published whenever a new user leaves a guild"""
    on_user_left = 'on_user_left'