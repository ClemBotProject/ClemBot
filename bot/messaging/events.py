"""
This module is to define all application level events in one place 
to avoid attempting to remember string event names
"""

class EventsMeta(type):
    """Class that defines what events are exposed at the bot level"""

    @property
    def on_example(self):
        """
        This is an example event for the Example Service, this should not be
        used under any circumstances

        Args:

            None
        """
        return 'on_example'

    @property
    def on_guild_message_received(self):
        """
        Published whenever a message is sent in a server
        
        Args:
            message (Message) – The deleted message.
        """
        return '_on_guild_message_received'

    @property
    def on_dm_message_received(self):
        """
        Published whenever a direct message is sent to ClemBot
        
        Args:
            message (Message) – The deleted message.
        """
        return '_on_dm_message_received'

    @property
    def on_raw_message_edit(self):
        """
        Published when a Message receives an update event and is not in the cache

        Args:

            payload (Edit Object) – The edit payload with the id of the edited message
        """
        return '_on_raw_message_edit'

    @property
    def on_message_edit(self):
        """
        Published when a Message receives an update event and is in the cache

        Args:

            before (Message) – The previous version of the message.
            after (Message) – The current version of the message.
        """
        return '_on_message_edit'

    @property
    def on_raw_message_delete(self):
        """
        Published when a Message receives an update event and is not in the cache

        Args:

            payload (Edit Object) – The delete payload with the id of the edited message
        """
        return '_on_raw_message_delete'

    @property
    def on_message_delete(self):
        """
        Published whenever a message is deleted while it exists in the cache

        Args:

            message (Message) – The message that was deleted
        """
        return '_on_message_delete'

    def on_reaction_add(self):
        """
        Published whenever a reaction is sent in a server, and that message is stored
        in d.pys internal cache

        Args:
            
            reaction (Reaction) – The current state of the reaction.
            user (Union[Member, User]) – The user who added the reaction.
        """
        return '_on_reaction_add'

    _on_raw_reaction_add = 'on_raw_reaction_add'
    @property
    def on_raw_reaction_add(self):
        """
        Called when a message has a reaction added. regardless of cache state

        Args:

            payload (RawReactionActionEvent) – The raw event payload data.
        """
        return '_on_raw_reaction_add'

    @property
    def on_reaction_remove(self):
        """
        Published whenever a reaction is removed in a server, and that message is stored
        in d.pys internal cache

        Args:

            reaction (Reaction) – The current state of the reaction.
            user (Union[Member, User]) – The user who removed the reaction.
        """
        return '_on_reaction_remove'

    @property
    def on_raw_reaction_remove(self):
        """
        Called when a message has a reaction removeed. regardless of cache state

        Args:

            payload (RawReactionActionEvent) – The raw event payload data.
        """
        return '_on_raw_reaction_remove'

    @property
    def on_guild_joined(self):
        """
        Published whenever the bot joins new guild

        Args:

            guild (Guild) – The guild that was joined.    
        """
        return '_on_guild_joined'

    @property
    def on_guild_leave(self):
        """
        Published whenever the bot leaves a guild

        Args:

            guild (Guild) – The guild that was left.    
        """
        return '_on_guild_leave'

    @property
    def on_new_guild_initialized(self):
        """
        Published whenever the bot joins a new guild and that guild has been created
        in the bots database. This is the event that should be used for all new guild
        related services

        Args:

            guild (Guild) – The guild that was joined.    
        """
        return '_on_new_guild_initialized'

    @property
    def on_guild_role_create(self):
        """
        published whenever a guild role is created in a guild
        
        Args:

            role (Role) – The role that was created or deleted.
        """
        return '_on_guild_role_create'

    @property
    def on_guild_role_update(self):
        """
        published whenever a guild role is updated in a guild
        
        Args:

            before (Role) – The updated role’s old info.
            after (Role) – The updated role’s updated info.
        """
        return '_on_guild_role_update'

    @property
    def on_guild_role_delete(self):
        """
        published whenever a guild role is deleted in a guild
        
        Args:

            role (Role) – The role that was created or deleted.
        """
        return '_on_guild_role_delete'

    @property
    def on_user_joined(self):
        """
        Published whenever a new user joins a guild
        
        Args:

            user (User) – The user who joined or left.
        """
        return '_on_user_joined'

    @property
    def on_user_removed(self):
        """
        Published whenever a user leaves a guild
        
        Args:

            user (User) – The user who was removed or left.
        """
        return '_on_user_removed'

    @property
    def on_user_update(self):
        """
        Published whenever a user updates themselves
        
        Args:

            before (User) – The updated user’s old info. 
            after (User) – The updated user’s updated info.
        """
        return '_on_user_update'

    @property
    def on_add_designated_channel(self):
        """
        Published whenever a designated channel id is added to a designated channel slot

        Args:

            channel (Channel) the channel object that was added
        """
        return '_on_add_designated_channel'

    @property
    def on_send_in_designated_channel(self):
        """
        Published when a reqeust to send a message in a designated channel is sent

        Args:

            channel_type (str) The designated channel to send the message in
            guild_id (int) The id of the guild to attempt to send a message in
            message (union[embed, str]) the message to be sent to the channel
            id [Optional] (int) Id to associate a sent dc message with sent message ids at the publish site
        """
        return 'on_send_in_designated_channel'

    @property
    def on_designated_message_sent(self):
        """
        Published when an on_send_in_designate_channel event is published with an optional id parameter, 
        this serves as a callback for that event to maintain seperation of concerns

        Args:

            dc_id (int) The id of the dc send event that was given to the dc service
            message (Union[discord.Message, list[discord.Message]]) the message or the list of The messages sent in dc channels
        """
        return 'on_designated_message_sent'

    @property
    def on_broadcast_designated_channel(self):
        """
        Published when a request to broadcast a message to all registered channels
        in all servers is sent

        Args:

            channel_type (str) The designated channel to broadcast the message to
            message (union[embed, str]) the message to be sent to the channels
        """
        return '_on_broadcast_designated_channel'
    
    @property
    def on_set_custom_prefix(self):
        """
        Published when a new custom prefix is added in a guild

        Args:

            guild (discord.Guild): The guild object of the added prefix
            prefix (str): The prefix to be added
        """
        return 'on_set_custom_prefix'
    
    @property
    def on_assignable_role_add(self):
        """
        Pulbished when a new role is marked as set to be marked as assignable

        Args:
            role (discord.Role) The role to mark as assignable
        """
        return 'on_assignable_role_add'

    @property
    def on_assignable_role_remove(self):
        """
        Pulbished when a role is marked as set to be removed as assignable

        Args:
            role (discord.Role) The role to remove as assignable
        """
        return 'on_assignable_role_remove'

    @property
    def on_set_deletable(self):
        """
        Published when a bot message is needed to be able to be deleted
        
        Args:
            messagesToDelete (List[discord.Message]) Messages to be deleted
            author (discord.Member) member who called the bot 
            roles (str) Stores the roles needed to delete the message
        """
        return '_on_set_deletable'
    
    @property
    def on_guild_channel_create(self):
        """
        Published when a new text channel is created in a guild

        Args:
            channel (discord.TextChannel): The new channel
        """
        return 'on_guild_channel_create'

    @property
    def on_guild_channel_delete(self):
        """
        Published when a new text channel is deleted in a guild

        Args:
            channel (discord.TextChannel): The deleted channel
        """
        return 'on_guild_channel_delete'

    @property
    def on_guild_channel_update(self):
        """
        Published when a text channel is edited

        Args:
            before (discord.TextChannel): The before of the channel
            after (discord.TextChannel): The after of the channel
        """
        return 'on_guild_channel_update'

    @property
    def on_set_pageable_text(self):
        """
        Published when a bot message is needed to be able to be paginate
        
        Args:
            embed_name (str): name of the embed
            field_title (str): name for the field/page 
            pages (list[str]): a list of every page/field for the embed
            author (discord.Member): member who called the bot 
            channel (discord.TextChannel): the channel to send the embed
            timeout (int): optional arg, time(seconds) for paginate to timeout, default is 60s 
        """
        return 'on_set_pageable_text'


    @property
    def on_set_pageable_embed(self):
        """
        Published when a listof embeds is needed to be able to paginate
        
        Args:
            pages (list[discord.Embed]): a list of embeds to scroll through
            author (discord.Member): member who called the bot 
            channel (discord.TextChannel): the channel to send the embed
            timeout (int): optional arg, time(seconds) for paginate to timeout, default is 60s 
        """
        return 'on_set_pageable_embed'
    
    @property
    def on_member_update(self, before, after):
        """
        This is called when one or more of the following things change:

            status
            activity
            nickname
            roles
            pending
        """
        return 'on_member_update'



class Events(metaclass= EventsMeta):
    pass