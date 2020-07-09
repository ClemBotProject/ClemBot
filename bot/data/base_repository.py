import logging

import aiosqlite

from bot.bot_secrets import BotSecrets

log = logging.getLogger(__name__)

class BaseRepository:
    """
    The base level repository that defines the fully resolved path for
    sqlite connection
    """

    def __init__(self):
        self.database_name = BotSecrets.get_instance().database_name
        self.resolved_db_path = f'database/{self.database_name}'

    async def fetcthall_as_dict(self, cursor: aiosqlite.Cursor):
        """
        This function returns a dictionary that contains the row names of the sql query
        as keys in a dictionary instead of the cursor result being index based which
        can be unclear and confusing

        Args:
            cursor (aiosqlite.Cursor): The cursor object that contains the query to be ran

        Returns:
            [dict]: a dictionary with row names as keys
        """
        return [dict(zip([column[0] for column in cursor.description], row))
                for row in await cursor.fetchall()]
