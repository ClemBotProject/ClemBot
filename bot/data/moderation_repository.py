from datetime import datetime
import typing as t

import aiosqlite

from bot.data.base_repository import BaseRepository
from bot.consts import Infractions


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
            duration: datetime):
        args = {
            'guild_id': guild_id,
            'author_id': author_id,
            'subject_id': subject_id,
            'reason': reason,
            'duration': duration,
            'i_type': Infractions.mute
        }
        await self._insert_infraction(**args)

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
            i_type: Infractions):
        async with aiosqlite.connect(self.resolved_db_path) as db:
            await db.execute(
                """
                INSERT INTO Infractions (fk_guildId, fk_authorId, fk_subjectId, iType, duration, reason) 
                VALUES (?, ?, ?, ?, ?, ?)
                """, (guild_id, author_id, subject_id, i_type, duration, reason))
            await db.commit()

    async def get_all_bans(self, guild_id):
        async with aiosqlite.connect(self.resolved_db_path) as db:
            async with db.execute("SELECT * FROM Infractions WHERE fk_guildId = ? and iType = 'ban'",
                    (guild_id,)) as c:
                return await self.fetcthall_as_class(c)

    async def get_all_mutes(self, guild_id):
        async with aiosqlite.connect(self.resolved_db_path) as db:
            async with db.execute("SELECT * FROM Infractions WHERE fk_guildId = ? and iType = 'mute'",
                    (guild_id,)) as c:
                return await self.fetcthall_as_class(c)

    async def get_all_warns(self, guild_id):
        async with aiosqlite.connect(self.resolved_db_path) as db:
            async with db.execute("SELECT * FROM Infractions WHERE fk_guildId = ? and iType = 'warn'",
                    (guild_id,)) as c:
                return await self.fetcthall_as_class(c)