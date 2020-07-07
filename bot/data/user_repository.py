import logging

import aiosqlite

from bot.data.base_repository import BaseRepository

log = logging.getLogger(__name__)
class UserRepository(BaseRepository):

    async def add_user(self, user: str, guild_id: int) -> None:
        if await self.check_user(user.id):
            return

        async with aiosqlite.connect(self.resolved_db_path) as db:
            await db.execute('INSERT INTO Users (id, fk_guildId, name) VALUES (?, ?, ?)', (user.id, guild_id, user.name))
            await db.execute('INSERT INTO Users_Guilds VALUES (?, ?)', (guild_id, user.id))
            await db.commit()

    async def check_user(self, user_id: int) -> bool:
        async with aiosqlite.connect(self.resolved_db_path) as db:
            async with db.execute('SELECT * FROM Users WHERE id = ?', (user_id,)) as c:
                return await c.fetchone() is not None
