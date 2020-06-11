import aiosqlite
import sqlite3
import logging

from bot.data.base_repository import BaseRepository
from bot.errors import PrimaryKeyError
log = logging.getLogger(__name__)
class UserRepository(BaseRepository):

    async def add_user(self, user: str, guild_id: int) -> None:
        try:
            async with aiosqlite.connect(self.resolved_db_path) as db:
                await db.execute('INSERT INTO Users (id, fk_guildId, name) VALUES (?, ?, ?)', (user.id, guild_id, user.name))
                await db.execute('INSERT INTO Users_Guilds VALUES (?, ?)', (guild_id, user.id))
                await db.commit()
        except sqlite3.IntegrityError as e:
            raise PrimaryKeyError(f'Failed to insert user: {e}')