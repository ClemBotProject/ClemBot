import aiosqlite

from bot.data.base_repository import BaseRepository


class LogoutRepository(BaseRepository):

    async def add_logout_date(self, time):
        async with aiosqlite.connect(self.resolved_db_path) as db:
            await db.execute(
                """
                INSERT INTO LogoutDates (date)
                VALUES (?)
                """, (time,))
            await db.commit()
