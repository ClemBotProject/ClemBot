from sqlite3.dbapi2 import converters
import aiosqlite
from discord.ext.commands.converter import Converter

from bot.data.base_repository import BaseRepository

class RemindRepository(BaseRepository):

    async def insert_reminder(self, user: int, message: int, link: str, time):
        async with aiosqlite.connect(self.resolved_db_path) as db:
            await db.execute(
                """
                INSERT INTO Reminders (fk_userId, fk_messageId, link, time) 
                VALUES (?, ?, ?, ?)
                """, (user, message, link, time,))
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

    async def query_reminder(self, fk_userId: int, fk_messageId: int):
        async with aiosqlite.connect(self.resolved_db_path) as db:
            async with db.execute('SELECT * FROM Reminders WHERE fk_userId = ? AND fk_messageId = ?',
                  (fk_userId, fk_messageId)) as c:
                return await self.fetcthone_as_dict(c)
        
    async def get_all_reminders(self):
        async with aiosqlite.connect(self.resolved_db_path) as db:
            async with db.execute('SELECT * FROM Reminders', ()) as c:
                result = await self.fetcthall_as_dict(c)
            return result