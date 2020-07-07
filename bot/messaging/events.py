"""
This module is to define all application level events in one place 
to avoid attempting to remember string event names
"""

class Events:
    """Class that defines what events are exposed at the bot level"""

    _on_message_recieved = 'on_message_recieved'
    @property
    def on_message_recieved(self):
        """
        Published whenever a message is sent in a server
        
        Args:
            message (Message) – The deleted message.
        """
        return self._on_message_recieved

    _on_message_edit = 'on_message_edit'
    @property
    def on_message_edit(self):
        """
        Published when a Message receives an update event and is in the cache

        Args:

            before (Message) – The previous version of the message.

            after (Message) – The current version of the message.
        """
        return self._on_message_edit

    _on_message_delete = 'on_message_delete'
    @property
    def on_message_delete(self):
        """
        Published whenever a message is deleted while it exists in the cache

        Args:
            message (Message) – The message that was deleted
        """
        return self._on_message_delete

    _on_reaction_add = 'on_reaction_add'
    @property
    def on_reaction_add(self):
        """"
        Published whenever a reaction is sent in a server, and that message is stored
        in d.pys internal cache

        Args:
            reaction (Reaction) – The current state of the reaction.
            user (Union[Member, User]) – The user who added the reaction.
        """
        return self._on_reaction_add

    _on_raw_reaction_add = 'on_raw_reaction_add'
    @property
    def on_raw_reaction_add(self):
        """
        Called when a message has a reaction added. regardless of cache state

        Args:
            payload (RawReactionActionEvent) – The raw event payload data.
        """
        return self._on_raw_reaction_add

    _on_reaction_remove = 'on_reaction_remove'
    @property
    def on_reaction_remove(self):
        """"
        Published whenever a reaction is removed in a server, and that message is stored
        in d.pys internal cache

        Args:
            reaction (Reaction) – The current state of the reaction.
            user (Union[Member, User]) – The user who removeed the reaction.
        """
        return self._on_reaction_remove

    _on_raw_reaction_remove = 'on_raw_reaction_remove'
    @property
    def on_raw_reaction_remove(self):
        """
        Called when a message has a reaction removeed. regardless of cache state

        Args:
            payload (RawReactionActionEvent) – The raw event payload data.
        """
        return self._on_raw_reaction_remove

    _on_guild_joined = 'on_guild_joined'
    @property
    def on_guild_joined(self):
        """"
        Published whenever the bot joins new guild

        Args:
            guild (Guild) – The guild that was joined.    
        """
        return self._on_guild_joined

    _on_guild_role_create = 'on_guild_role_create'
    @property
    def on_guild_role_create(self):
        """"
        published whenever a guild role is created in a guild
        
        Args:
            role (Role) – The role that was created or deleted.
        """
        return self._on_guild_role_create

    _on_guild_role_update = 'on_guild_role_update'
    @property
    def on_guild_role_update(self):
        """"
        published whenever a guild role is updated in a guild
        
        Args:
            before (Role) – The updated role’s old info.
            after (Role) – The updated role’s updated info.
        """
        return self._on_guild_role_update

    _on_guild_role_delete = 'on_guild_role_delete'
    @property
    def on_guild_role_delete(self):
        """"
        published whenever a guild role is deleted in a guild
        
        Args:
            role (Role) – The role that was created or deleted.
        """
        return self._on_guild_role_delete

    _on_user_joined = 'on_user_joined'
    @property
    def on_user_joined(self):
        """"
        Published whenever a new user joins a guild
        
        Args:
            user (User) – The user who joined or left.
        """
        return self._on_user_joined

    _on_user_left = 'on_user_left'
    @property
    def on_user_left(self):
        """"
        Published whenever a user leaves a guild
        
        Args:
            user (User) – The user who joined or left.
        """
        return self._on_user_left

    _on_user_update = 'on_user_update'
    @property
    def on_user_update(self):
        """"
        Published whenever a user updates themselves
        
        Args:
            before (User) – The updated user’s old info. 
            after (User) – The updated user’s updated info.
        """
        return self._on_user_update

    _on_add_designated_channel = 'on_add_designated_channel'
    @property
    def on_add_designated_channel(self):
        """
        Published whenever a designated channel id is added to a designated channel slot

        Args:
            channel (Channel) the channel object that was added
        """
        return self._on_add_designated_channel

    _on_send_in_designated_channel = 'on_send_in_designated_channel'
    @property
    def on_send_in_designated_channel(self):
        """
        Published when a reqeust to send a message in a designated channel is sent

        Args:
            channel_type (str) The designated channel to send the message in
            message (union[embed, str]) the message to be sent to the channel
        """
        return self._on_send_in_designated_channel