import logging
import os

import aiosqlite

log = logging.getLogger(__name__)


class Database:

    def __init__(self, name: str):
        self.database_name = name

    async def create_database(self):
        if not os.path.exists('database'):
            log.info('Database Folder not found: Creating one')
            os.makedirs('database')
        async with aiosqlite.connect(f'database/{self.database_name}') as db:
            #db.row_factory = aiosqlite.Row
            with open('bot/data/CreateTables.sql') as f:
                await db.executescript(f.read())
                await db.commit()
