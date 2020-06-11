import aiosqlite

from bot.data.base_repository import BaseRepository


class MessageRepository(BaseRepository):

    async def add_message(self, message):
        async with aiosqlite.connect(self.resolved_db_path) as db:
            await db.execute(
                """
                INSERT INTO Messages
                (id, fk_guildId, fk_channelId, fk_authorId, content)
                VALUES
                (?, ?, ?, ?, ?)
                """, (message.id, message.guild.id, message.channel.id, message.author.id, message.content))
            await db.commit()

