import aiosqlite

from bot.data.base_repository import BaseRepository


class CustomPrefixesRepository(BaseRepository):

    async def set_prefix(self, guild_id: int, prefix: str) -> None:
        async with aiosqlite.connect(self.resolved_db_path) as db:
            await db.execute(
                """
                INSERT INTO CustomPrefixes VALUES (?, ?)
                ON CONFLICT(fk_guildId) DO UPDATE SET
                    prefix = excluded.prefix
                """, (guild_id, prefix))
            await db.commit()


