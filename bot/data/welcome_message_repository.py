import typing as t

import aiosqlite
import discord

from bot.data.base_repository import BaseRepository


class WelcomeMessageRepository(BaseRepository):

    async def set_welcome_message(self, guild: discord.Guild, message: str):
        async with aiosqlite.connect(self.resolved_db_path) as db:
            await db.execute(
                """
                INSERT INTO WelcomeMessages (fk_guildId, content) VALUES (?, ?)
                ON CONFLICT (fk_guildId) DO UPDATE SET
                    content = excluded.content
                """, (guild.id, message))
            await db.commit()

    async def delete_welcome_message(self, guild: discord.Guild):
        async with aiosqlite.connect(self.resolved_db_path) as db:
            await db.execute(
                """
                DELETE FROM WelcomeMessages
                WHERE fk_guildId = ?
                """, (guild.id,))
            await db.commit()

    async def get_welcome_message(self, guild_id) -> t.Union[str, None]:
        async with aiosqlite.connect(self.resolved_db_path) as db:
            async with db.execute('SELECT content FROM WelcomeMessages WHERE fk_guildId = ?',
                                  (guild_id,)) as c:
                mes = await c.fetchone()
                return mes[0] if mes else None
