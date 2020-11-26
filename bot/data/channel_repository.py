import aiosqlite
import logging

import discord

from bot.data.base_repository import BaseRepository

log = logging.getLogger(__name__)


class ChannelRepository(BaseRepository):

    async def add_channel(self, channel: discord.TextChannel) -> None:
        if await self.check_channel(channel.id):
            return

        async with aiosqlite.connect(self.resolved_db_path) as db:
            values = (channel.id, channel.guild.id , channel.name)
            await db.execute('INSERT INTO Channels (id, fk_guildId, name) VALUES (?, ?, ?)', values)
            await db.commit()

    async def delete_channel(self, channel: discord.TextChannel) -> None:
        async with aiosqlite.connect(self.resolved_db_path) as db:
            await db.execute('DELETE FROM Channels WHERE id = ?', (channel.id,))
            await db.commit()
    
    async def update_channel(self, after):
        async with aiosqlite.connect(self.resolved_db_path) as db:
            await db.execute(
                """
                INSERT INTO Channels (id, fk_guildId, name) VALUES (?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    name = excluded.name
                """, (after.id, after.guild.id, after.name))
            await db.commit()

    async def check_channel(self, channel_id: int) -> bool:
        async with aiosqlite.connect(self.resolved_db_path) as db:
            async with db.execute('SELECT * FROM Channels WHERE id = ?', (channel_id,)) as c:
                return await c.fetchone() is not None