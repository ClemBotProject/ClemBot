import logging
import typing as t

import aiosqlite

from bot.data.base_repository import BaseRepository

log = logging.getLogger(__name__)


class GuildRepository(BaseRepository):

    async def add_guild(self, guild) -> None:
        if await self.check_guild(guild.id):
            await self.set_guild_status(guild.id, True)
            return

        async with aiosqlite.connect(self.resolved_db_path) as db:
            await db.execute('INSERT INTO Guilds VALUES (?, ?, ?)', (guild.id, guild.name, True))
            await db.commit()

    async def get_all_guilds_ids(self) -> t.List[int]:
        async with aiosqlite.connect(self.resolved_db_path) as db:
            async with db.execute('SELECT id FROM Guilds') as c:
                return [i[0] for i in await c.fetchall()]

    async def set_guild_status(self, guild_id: int, status: bool) -> None:
        async with aiosqlite.connect(self.resolved_db_path) as db:
            await db.execute('UPDATE Guilds SET active = ? WHERE id = ?', (status, guild_id))
            await db.commit()

    async def check_guild(self, guild_id: int) -> bool:
        async with aiosqlite.connect(self.resolved_db_path) as db:
            async with db.execute('SELECT * FROM Guilds WHERE id = ?', (guild_id,)) as c:
                return await c.fetchone() is not None

    async def get_guild_count(self) -> int:
        async with aiosqlite.connect(self.resolved_db_path) as db:
            async with db.execute('SELECT count(*) FROM Guilds') as c:
                return (await c.fetchone())[0]

    async def get_active_guild_count(self) -> int:
        async with aiosqlite.connect(self.resolved_db_path) as db:
            async with db.execute('SELECT count(*) FROM Guilds WHERE active = true') as c:
                return (await c.fetchone())[0]
