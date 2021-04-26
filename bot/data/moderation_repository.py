import typing as t
from datetime import datetime

import aiosqlite

from bot.consts import Infractions
from bot.data.base_repository import BaseRepository


class ModerationRepository(BaseRepository):

    async def insert_ban(self, *,
                         guild_id: int,
                         author_id: int,
                         subject_id: int,
                         reason: str):
        args = {
            'guild_id': guild_id,
            'author_id': author_id,
            'subject_id': subject_id,
            'reason': reason,
            'i_type': Infractions.ban
        }
        await self._insert_infraction(**args)

    async def insert_mute(self, *,
                          guild_id: int,
                          author_id: int,
                          subject_id: int,
                          reason: t.Optional[str] = None,
                          duration: datetime) -> int:
        args = {
            'guild_id': guild_id,
            'author_id': author_id,
            'subject_id': subject_id,
            'reason': reason,
            'duration': duration,
            'i_type': Infractions.mute,
            'active': True
        }
        return await self._insert_infraction(**args)

    async def insert_warn(self, *,
                          guild_id: int,
                          author_id: int,
                          subject_id: int,
                          reason: str):
        args = {
            'guild_id': guild_id,
            'author_id': author_id,
            'subject_id': subject_id,
            'reason': reason,
            'i_type': Infractions.warn
        }
        await self._insert_infraction(**args)

    async def _insert_infraction(self, *,
                                 guild_id: int,
                                 author_id: int,
                                 subject_id: int,
                                 reason: t.Optional[str] = None,
                                 duration: t.Optional[datetime] = None,
                                 i_type: Infractions,
                                 active=None) -> int:
        async with aiosqlite.connect(self.resolved_db_path) as db:
            async with db.execute(
                    """
                INSERT INTO Infractions (fk_guildId, fk_authorId, fk_subjectId, iType, duration, reason, active, time) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                    (guild_id, author_id, subject_id, i_type, duration, reason, active, datetime.now())) as c:
                id = c.lastrowid
            await db.commit()
            return id

    async def check_infraction(self, guild_id: int, infra_id: int) -> bool :
        async with aiosqlite.connect(self.resolved_db_path) as db:
            async with db.execute('SELECT * FROM Infractions WHERE id = ? AND fk_guildId = ?',
                                  (infra_id, guild_id)) as c:
                return await c.fetchone() is not None

    async def delete_infractions(self, guild_id: int, infra_id: int):
        async with aiosqlite.connect(self.resolved_db_path) as db:
            await db.execute('DELETE FROM Infractions WHERE id = ? AND fk_guildId = ?',
                             (infra_id, guild_id))
            await db.commit()

    async def deactivate_mute(self, id):
        async with aiosqlite.connect(self.resolved_db_path) as db:
            await db.execute('UPDATE Infractions SET active = ? WHERE id = ?', (False, id))
            await db.commit()

    async def get_all_bans(self, guild_id):
        async with aiosqlite.connect(self.resolved_db_path) as db:
            async with db.execute(f"SELECT * FROM Infractions WHERE fk_guildId = ? AND iType = '{Infractions.ban}'",
                                  (guild_id,)) as c:
                return await self.fetcthall_as_class(c)

    async def get_all_mutes(self, guild_id):
        async with aiosqlite.connect(self.resolved_db_path) as db:
            async with db.execute(f"SELECT * FROM Infractions WHERE fk_guildId = ? AND iType = '{Infractions.mute}'",
                                  (guild_id,)) as c:
                return await self.fetcthall_as_class(c)

    async def get_all_active_mutes(self, guild_id):
        async with aiosqlite.connect(self.resolved_db_path) as db:
            async with db.execute(f"SELECT * FROM Infractions WHERE fk_guildId = ? AND iType = '{Infractions.mute}' AND active = true",
                                  (guild_id,)) as c:
                return await self.fetcthall_as_class(c)

    async def get_all_active_mutes_member(self, guild_id, member_id):
        async with aiosqlite.connect(self.resolved_db_path) as db:
            async with db.execute(f"""
                                        SELECT * FROM Infractions 
                                        WHERE fk_guildId = ? 
                                        AND fk_subjectId = ? 
                                        AND iType = '{Infractions.mute}'
                                        AND active = ?
                                        """,
                                  (guild_id, member_id, True)) as c:
                return await self.fetcthall_as_class(c)

    async def get_all_warns_guild(self, guild_id):
        async with aiosqlite.connect(self.resolved_db_path) as db:
            async with db.execute(f"SELECT * FROM Infractions WHERE fk_guildId = ? AND iType = '{Infractions.warn}'",
                                  (guild_id,)) as c:
                return await self.fetcthall_as_class(c)

    async def get_all_warns_member(self, guild_id, member_id):
        async with aiosqlite.connect(self.resolved_db_path) as db:
            async with db.execute(f"""
                                    SELECT * FROM Infractions 
                                    WHERE fk_guildId = ? 
                                    AND fk_subjectId = ? 
                                    AND iType = '{Infractions.warn}'
                                    """,
                                  (guild_id, member_id)) as c:
                return await self.fetcthall_as_class(c)

    async def get_all_infractions_member(self, guild_id, member_id):
        async with aiosqlite.connect(self.resolved_db_path) as db:
            async with db.execute(f"""
                                    SELECT * FROM Infractions 
                                    WHERE fk_guildId = ? 
                                    AND fk_subjectId = ? 
                                    """,
                                  (guild_id, member_id)) as c:
                return await self.fetcthall_as_class(c)
