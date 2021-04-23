import logging

import aiosqlite
import discord

from bot.data.base_repository import BaseRepository

log = logging.getLogger(__name__)


class UserRepository(BaseRepository):

    async def add_user(self, user: discord.Member, guild_id: int) -> None:
        """
        Adds a User to the global users table and/or to the guild specific user tables

        Args:
            user (discord.Member)
            guild_id (int)
        """

        if await self.check_user_guild(guild_id, user.id):
            return

        async with aiosqlite.connect(self.resolved_db_path) as db:

            if not await self.check_global_user(user.id):
                await db.execute('INSERT INTO Users (id, name) VALUES (?, ?)', (user.id, user.name))

            await db.execute('INSERT INTO Users_Guilds VALUES (?, ?)', (guild_id, user.id))
            await db.commit()

    async def check_global_user(self, user_id: int) -> bool:
        """
        Checks if the user is in the global users table

        Args:
            user_id (int)

        Returns:
            bool
        """
        async with aiosqlite.connect(self.resolved_db_path) as db:
            async with db.execute('SELECT * FROM Users WHERE id = ?', (user_id,)) as c:
                return await c.fetchone() is not None

    async def check_user_guild(self, guild_id: int, user_id: int) -> bool:
        """
        Checks if a specific user is a logged member of a certain guild

        Args:
            guild_id (int)
            user_id (int)

        Returns:
            bool
        """
        async with aiosqlite.connect(self.resolved_db_path) as db:
            async with db.execute(
                    """
                    SELECT * FROM Users_Guilds 
                    WHERE fk_guildId = ? and fk_userId = ?
                    """, (guild_id, user_id)) as c:
                return await c.fetchone() is not None

    async def get_user_count(self, guild_id: int = None) -> int:
        async with aiosqlite.connect(self.resolved_db_path) as db:
            try:
                if guild_id:
                    c = await db.execute('SELECT count(*) FROM Users_Guilds WHERE fk_guildId = ?', (guild_id,))
                else:
                    c = await db.execute('SELECT count(*) FROM Users')
                return (await c.fetchone())[0]
            finally:
                c.close()
