import aiosqlite
import logging

from bot.data.base_repository import BaseRepository
log = logging.getLogger(__name__)


class GuildRepository(BaseRepository):

    async def add_guild(self, guild) -> None:
        if await self.check_guild(guild.id): 
            return 

        async with aiosqlite.connect(self.resolved_db_path) as db:
            await db.execute('INSERT INTO Guilds VALUES (?, ?)', (guild.id, guild.name))
            await db.commit()

            for c in guild.channels:
                await self.add_channel(c, guild.id)

    async def add_channel(self, channel, guild_id) -> None:
        if await self.check_channel(channel.id):
            return

        async with aiosqlite.connect(self.resolved_db_path) as db:
            values = (channel.id, guild_id, channel.name)
            await db.execute('INSERT INTO Channels (id, fk_guildId, name) VALUES (?, ?, ?)', values)
            await db.commit()

    async def check_guild(self, guild_id: int) -> bool:
        async with aiosqlite.connect(self.resolved_db_path) as db:
            async with db.execute('SELECT * FROM Guilds WHERE id = ?', (guild_id,)) as c:
                return await c.fetchone() is not None

    async def check_channel(self, channel_id: int) -> bool:
        async with aiosqlite.connect(self.resolved_db_path) as db:
            async with db.execute('SELECT * FROM Channels WHERE id = ?', (channel_id,)) as c:
                return await c.fetchone() is not None