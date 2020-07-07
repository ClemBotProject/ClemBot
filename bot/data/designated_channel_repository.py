from typing import List

import aiosqlite

from bot.data.base_repository import BaseRepository
from bot.errors import DesignatedChannelError


class DesignatedChannelRepository(BaseRepository):

    async def get_all_assigned_channels(self, designated_name) -> List[int]:
        """
        Gets all the channels assigned to a specifc designation

        Args:
            designated_name ([type]): the string name of the designated channel

        Returns:
            List[int]: A list of ids of all registered channels
        """
        designated_id = await self.get_designated_id(designated_name)
        async with aiosqlite.connect(self.resolved_db_path) as db:
            async with db.execute(
                    """
                    SELECT * FROM DesignatedChannels_Channels 
                    WHERE fk_designatedChannelsId = ?
                    """, (designated_id,)) as c:
                result = await c.fetchall()
                return [v for _, v in result]

    async def get_all_designated_channels(self):
        """
        Gets all currently defined designated channels 

        Returns:
            [type]: A list of tuples that contain (id, name)
        """

        async with aiosqlite.connect(self.resolved_db_path) as db:
            async with db.execute('SELECT * FROM DesignatedChannels') as c:
                result = await c.fetchall()
                return result

    async def register_designated_channel(self, channel_type: str, added_channel) -> None:
        """
        Registers an active channel with a designated channel category

        Args:

            channel_type (str): The string name of the designated channel

            added_channel (discord.TextChannel): The active text channel to register

        Raises:

            DesignatedChannelError: Raised when the designated channel type doesnt exit

            DesignatedChannelError: Raised when the TextChannel has already been registered to 
            this designated channel type
        """        
        
        if not await self.check_designated_channel(channel_type):
            raise DesignatedChannelError(f'The designated channel type {channel_type} does not exist')

        designated_id = await self.get_designated_id(channel_type)
        
        if await self.check_channel_added(designated_id, added_channel.id):
            raise DesignatedChannelError(f'{added_channel.name} is already assigned to {channel_type}')

        async with aiosqlite.connect(self.resolved_db_path) as db:
            await db.execute(
                """
                INSERT INTO DesignatedChannels_Channels
                VALUES (?, ?)
                """, (designated_id, added_channel.id))
            await db.commit()

    async def add_designated_channel_type(self, channel_type: str) -> None:
        """
        Args:
            channel_type (str): The name of the designated_channel to add
        """        
        if await self.check_designated_channel(channel_type):
            return

        async with aiosqlite.connect(self.resolved_db_path) as db:
            await db.execute(
                """
                INSERT INTO DesignatedChannels (name)
                VALUES (?)
                """, (channel_type,))
            await db.commit()

    async def remove_from_designated_channel(self, channel_type: str, channel_id) -> None:
        """
        Removes a given TextChannel from the list of active designated channel listeners

        Args:

            channel_type (str): The string name of the designated channel to be removed from

            channel_id ([type]): The id of the channel to deregister

        Raises:

            DesignatedChannelError: Raised when the designated channel type doesnt exit

            DesignatedChannelError: Raised when the given channel id is not currently registered to that designated channel
        """        

        if not await self.check_designated_channel(channel_type):
            raise DesignatedChannelError(f'The designated channel type {channel_type} does not exist')

        designated_id = await self.get_designated_id(channel_type)

        if not await self.check_channel_added(designated_id, channel_id):
            raise DesignatedChannelError(f'{channel_id} is not present in {channel_type}')

        designated_id = await self.get_designated_id(channel_type)

        async with aiosqlite.connect(self.resolved_db_path) as db:
            await db.execute(
                """
                DELETE FROM DesignatedChannels_Channels
                WHERE fk_designatedChannelsId = ? and fk_channelsId = ?
                """, (designated_id, channel_id,))
            await db.commit()

    async def get_designated_id(self, name):
        """
        Takes a designated name and returns the associated auto incremented id 

        Args:
            name (str): The string name of the designated channel

        Returns:
            int: the integer id of the designated channel
        """        
        async with aiosqlite.connect(self.resolved_db_path) as db:
            async with db.execute(
                    """ 
                    SELECT id FROM DesignatedChannels
                    WHERE name = ?
                    """, (name,)) as c:
                (designated_id,) = await c.fetchone()
                return designated_id

    async def check_channel_added(self, designated_channel_id, added_channel_id) -> bool:
        async with aiosqlite.connect(self.resolved_db_path) as db:
            async with db.execute(
                    """ 
                    SELECT * FROM DesignatedChannels_Channels
                    WHERE fk_channelsId = ? and fk_designatedChannelsId = ?
                    """, (added_channel_id, designated_channel_id)) as c:
                return await c.fetchone() is not None

    async def check_designated_channel(self, designated_name: int) -> bool:
        async with aiosqlite.connect(self.resolved_db_path) as db:
            async with db.execute(
                    """
                    SELECT * FROM DesignatedChannels WHERE name = ?
                    """, (designated_name,)) as c:
                return await c.fetchone() is not None
