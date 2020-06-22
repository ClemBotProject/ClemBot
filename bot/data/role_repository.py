import aiosqlite

from bot.data.base_repository import BaseRepository


class RoleRepository(BaseRepository):

    async def add_role(self, role: str, guild_id: int) -> None:
        if await self.check_role(role.id):
            return

        async with aiosqlite.connect(self.resolved_db_path) as db:
            await db.execute(
                """
                INSERT INTO Roles (id, fk_guildId, name, position) VALUES (?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    name = excluded.name,
                    position = excluded.position
                """, (role.id, guild_id, role.name, role.position))
            await db.commit()

    async def check_role(self, role_id: int) -> bool:
        async with aiosqlite.connect(self.resolved_db_path) as db:
            async with db.execute('SELECT * FROM Roles WHERE id = ?', (role_id,)) as c:
                return await c.fetchone() is not None

