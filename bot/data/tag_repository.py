import aiosqlite

from bot.data.base_repository import BaseRepository


class TagRepository(BaseRepository):

    async def insert_tag(self, tag):
        async with aiosqlite.connect(self.resolved_db_path) as db:
            await db.execute(
                """
                INSERT INTO Tags (name, content, CreationDate, fk_GuildId, fk_UserId) 
                VALUES (?, ?, ?, ?, ?)
                """, (tag.name, tag.content, tag.creation_date, tag.guild_id, tag.user_id))
            await db.commit()

    async def delete_tag(self, name, guild_id):
        async with aiosqlite.connect(self.resolved_db_path) as db:
            await db.execute(
                """
                DELETE FROM Tags WHERE name = ? AND fk_GuildId = ?
                """, (name, guild_id))
            await db.commit()

    async def check_tag_exists(self, name: str, guild_id) -> bool:
        async with aiosqlite.connect(self.resolved_db_path) as db:
            async with db.execute('SELECT * FROM Tags WHERE name = ? AND fk_GuildId= ?',
                                  (name, guild_id)) as c:
                return await c.fetchone() is not None

    async def increment_tag_use_counter(self, name: str, guild_id: int) -> str:
        async with aiosqlite.connect(self.resolved_db_path) as db:
            await db.execute('UPDATE Tags SET useCount = useCount + 1 WHERE name = ? AND fk_guildId = ?', (name, guild_id,))
            await db.commit()

    async def get_tag_content(self, name: str, guild_id: int) -> str:
        async with aiosqlite.connect(self.resolved_db_path) as db:
            async with db.execute('SELECT Content FROM Tags WHERE name = ? AND fk_guildId = ?',
                                  (name, guild_id,)) as c:
                return (await self.fetcthone_as_dict(c))['content']

    async def get_tag(self, name: str, guild_id: int) -> str:
        async with aiosqlite.connect(self.resolved_db_path) as db:
            async with db.execute('SELECT * FROM Tags WHERE name = ? AND fk_guildId = ?',
                                  (name, guild_id,)) as c:
                return await self.fetcthone_as_dict(c)

    async def get_all_server_tags(self, guild_id: int) -> str:
        async with aiosqlite.connect(self.resolved_db_path) as db:
            async with db.execute(
                    """
                    SELECT * FROM Tags 
                    WHERE fk_guildId = ? 
                    ORDER BY name
                    """,
                    (guild_id,)) as c:
                return await self.fetcthall_as_dict(c)
