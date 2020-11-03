import aiosqlite
import logging

from bot.data.base_repository import BaseRepository
from bot.data.channel_repository import ChannelRepository
log = logging.getLogger(__name__)


class GuildRepository(BaseRepository):

    async def add_guild(self, guild) -> None:
        if await self.check_guild(guild.id): 
            return 

        async with aiosqlite.connect(self.resolved_db_path) as db:
            await db.execute('INSERT INTO Guilds VALUES (?, ?)', (guild.id, guild.name))
            await db.commit()

    async def check_guild(self, guild_id: int) -> bool:
        async with aiosqlite.connect(self.resolved_db_path) as db:
            async with db.execute('SELECT * FROM Guilds WHERE id = ?', (guild_id,)) as c:
                return await c.fetchone() is not None
            
    async def get_guild_count(self) -> int:
        async with aiosqlite.connect(self.resolved_db_path) as db:
            async with db.execute('SELECT count(*) FROM Guilds') as c:
                return (await c.fetchone())[0]
