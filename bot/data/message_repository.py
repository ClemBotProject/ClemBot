import aiosqlite

from bot.data.base_repository import BaseRepository


class MessageRepository(BaseRepository):

    async def add_message(self, message):
        if await self.check_message(message.id):
            return

        async with aiosqlite.connect(self.resolved_db_path) as db:
            await db.execute(
                """
                INSERT INTO Messages
                (id, fk_guildId, fk_channelId, fk_authorId, content)
                VALUES
                (?, ?, ?, ?, ?)
                """, (message.id, message.guild.id, message.channel.id, message.author.id, message.content))
            await db.commit()

    async def check_message(self, message: int) -> bool:
        async with aiosqlite.connect(self.resolved_db_path) as db:
            async with db.execute('SELECT * FROM Messages WHERE id = ?', (guild_id,)) as c:
                return await c.fetchone() is not None
