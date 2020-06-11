import aiosqlite
import sqlite3
import logging

from bot.data.base_repository import BaseRepository
from bot.errors import PrimaryKeyError
log = logging.getLogger(__name__)


class GuildRepository(BaseRepository):

    async def add_guild(self, guild):
        try:
            async with aiosqlite.connect(self.resolved_db_path) as db:
                await db.execute('INSERT INTO Guilds VALUES (?, ?)', (guild.id, guild.name))
                await db.commit()

                for c in guild.channels:
                    await self.add_channel(c, guild.id)
                
        except sqlite3.IntegrityError:
            raise PrimaryKeyError(f'Failed to insert guild, primary key failure, id: {guild.id}')
    
    async def add_channel(self, channel, guild_id):
        async with aiosqlite.connect(self.resolved_db_path) as db:
            values = (channel.id, guild_id, channel.name)
            await db.execute('INSERT INTO Channels (id, fk_guildId, name) VALUES (?, ?, ?)', values)
            await db.commit()
