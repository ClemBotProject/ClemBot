import aiosqlite
from cryptography.fernet import Fernet

from bot.bot_secrets import BotSecrets
from bot.data.base_repository import BaseRepository


def _encrypt_message(message: str):
    fernet = Fernet(BotSecrets.get_instance().message_encryption_key)
    return fernet.encrypt(message.encode())


def _decrypt_message(message: str):
    fernet = Fernet(bytes(BotSecrets.get_instance().message_encryption_key))
    return fernet.decrypt(bytes(message)).decode()


class MessageRepository(BaseRepository):

    async def add_message(self, message, time):
        if await self.check_message(message.id):
            return

        async with aiosqlite.connect(self.resolved_db_path) as db:
            content = _encrypt_message(message.content)

            # Message deletion to comply with discords message retention policies
            await db.execute("DELETE FROM Messages WHERE Time <= date('now','-30 day')")
            await db.execute(
                """
                INSERT INTO Messages
                (id, fk_guildId, fk_channelId, fk_authorId, content, time)
                VALUES
                (?, ?, ?, ?, ?, ?)
                """, (message.id, message.guild.id, message.channel.id, message.author.id, content, time))
            await db.commit()

    async def edit_message_content(self, message_id, content):
        content = _encrypt_message(content)

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

    async def get_message_count(self, guild_id: int = None) -> int:
        async with aiosqlite.connect(self.resolved_db_path) as db:
            try:
                if guild_id:
                    c = await db.execute('SELECT count(*) FROM Messages WHERE fk_guildId = ?', (guild_id,))
                else:
                    c = await db.execute('SELECT count(*) FROM Messages')
                return (await c.fetchone())[0]
            finally:
                c.close()

    async def get_message(self, message_id):
        if not await self.check_message(message_id):
            return None

        async with aiosqlite.connect(self.resolved_db_path) as db:
            async with db.execute('SELECT * FROM Messages WHERE id = ?', (message_id,)) as c:
                message = await self.fetcthone_as_dict(c)

        message['content'] = _decrypt_message(message['content'])
        return message

    async def check_message(self, message_id: int) -> bool:
        async with aiosqlite.connect(self.resolved_db_path) as db:
            async with db.execute('SELECT * FROM Messages WHERE id = ?', (message_id,)) as c:
                return await c.fetchone() is not None

    async def get_user_message_count(self, user_id, guild_id) -> int:
        async with aiosqlite.connect(self.resolved_db_path) as db:
            async with db.execute('SELECT count(*) FROM Messages WHERE fk_guildId = ? AND fk_authorId = ?', (guild_id, user_id,)) as c:
                return (await c.fetchone())[0]
            
    async def get_user_message_count_range(self, user_id, guild_id, days: int) -> int:
        if not isinstance(days, int):
            raise TypeError("Days parameter must be an int")
        async with aiosqlite.connect(self.resolved_db_path) as db:
            c = await db.execute(f'SELECT count(*) FROM Messages WHERE fk_guildId = ? AND fk_authorId = ? AND strftime("%Y-%m-%d", time) >= date("now","{-days} days")', (guild_id, user_id,))
            return (await c.fetchone())[0]