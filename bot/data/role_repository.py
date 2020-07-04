import aiosqlite
import logging

from bot.data.base_repository import BaseRepository
from bot.errors import PrimaryKeyError
log = logging.getLogger(__name__)

class RoleRepository(BaseRepository):

    async def add_or_update_role(self, role: str, guild_id: int) -> None:
        async with aiosqlite.connect(self.resolved_db_path) as db:
            await db.execute(
                """
                INSERT INTO Roles (id, fk_guildId, name, position) VALUES (?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    name = excluded.name,
                    position = excluded.position
                """, (role.id, guild_id, role.name, role.position))
            await db.commit()

    async def delete_role(self, role_id: int) -> None:
        if await self.check_role(role_id):
            async with aiosqlite.connect(self.resolved_db_path) as db:
                await db.execute(
                    """
                    DELETE FROM Roles 
                    WHERE id = ?
                    """, (role_id,))
                await db.commit()
    
    async def get_role_ids(self, guild_id):
        async with aiosqlite.connect(self.resolved_db_path) as db:
            async with db.execute('SELECT (id) FROM Roles WHERE fk_guildid = ?', (guild_id,)) as c:
                return await c.fetchall()

    async def drop_roles_table(self):
        async with aiosqlite.connect(self.resolved_db_path) as db:
            await db.execute("""DROP TABLE IF EXISTS Roles""")
            await db.commit()

    async def check_role(self, role_id: int) -> bool:
        async with aiosqlite.connect(self.resolved_db_path) as db:
            async with db.execute('SELECT * FROM Roles WHERE id = ?', (role_id,)) as c:
                return await c.fetchone() is not None
