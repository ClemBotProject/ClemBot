import aiosqlite

from bot.data.base_repository import BaseRepository

class RemindRepository(BaseRepository):

    async def insert_reminder(self, id: str, user: int, message: str, link: str, time):
        async with aiosqlite.connect(self.resolved_db_path) as db:
            await db.execute(
                """
                INSERT INTO Reminders (id, user, message, link, time) 
                VALUES (?, ?, ?, ?, ?)
                """, (id, user, message, link, time,))
            await db.commit()
    
    async def delete_reminder(self, id):
        async with aiosqlite.connect(self.resolved_db_path) as db:
            await db.execute(
                """
                DELETE FROM Reminders WHERE id = ?
                """, (id,))
            await db.commit()
    
    async def get_reminder(self, id: str) -> str:
        async with aiosqlite.connect(self.resolved_db_path) as db:
            async with db.execute('SELECT * FROM Reminders WHERE id = ?',
                    (id,)) as c:
                return await self.fetcthone_as_dict(c)

    async def get_all_reminders(self):
        async with aiosqlite.connect(self.resolved_db_path) as db:
            async with db.execute('SELECT * FROM Reminders', ()) as c:
                result = await c.fetchall()
            temp = [(i, u, m, l, t) for i, u, m, l, t in result]
            return temp