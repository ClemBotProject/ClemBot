import aiosqlite
from typing import Iterator


class Database:

    def __init__(self, name):
        self.database_name = name

    async def create_database(self) -> bool:
        async with aiosqlite.connect(self.database_name) as db:
            with open('bot/data/CreateTables.sql') as f:
                await db.executescript(f.read())
                await db.commit()
