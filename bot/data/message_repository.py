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

    async def edit_message_content(self, message_id, content):
        if not await self.check_message(message_id):
            return

        async with aiosqlite.connect(self.resolved_db_path) as db:
            await db.execute(
                """
                UPDATE Messages
                SET Content = ?
                WHERE id = ?
                """, (content, message_id))
            await db.commit()

    async def set_message_deletion(self, message_id):
        if not await self.check_message(message_id):
            return

        async with aiosqlite.connect(self.resolved_db_path) as db:
            await db.execute(
                """
                UPDATE Messages
                SET isDeleted = true
                WHERE id = ?
                """, (message_id,))
            await db.commit()

    async def get_message(self, message_id):
        if not await self.check_message(message_id):
            return None

        async with aiosqlite.connect(self.resolved_db_path) as db:
            async with db.execute('SELECT * FROM Messages WHERE id = ?', (message_id,)) as c:
                return await self.fetcthone_as_dict(c)

    async def check_message(self, message_id: int) -> bool:
        async with aiosqlite.connect(self.resolved_db_path) as db:
            async with db.execute('SELECT * FROM Messages WHERE id = ?', (message_id,)) as c:
                return await c.fetchone() is not None
