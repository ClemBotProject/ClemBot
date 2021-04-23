import logging

import aiosqlite
import discord

from bot.consts import Claims
from bot.data.base_repository import BaseRepository

log = logging.getLogger(__name__)


class ClaimsRepository(BaseRepository):

    async def fetch_all_claims_user(self, user: discord.Member):
        claims = set()
        for r in user.roles:
            async with aiosqlite.connect(self.resolved_db_path) as db:
                async with db.execute(
                        """
                        SELECT claimName FROM ClaimsMapping
                        WHERE fk_roleId = ?
                        """, (r.id,)) as c:
                    role_claims = await self.fetcthall_as_dict(c)
                    if len(role_claims) == 0:
                        continue
                    claims.update([c['claimName'] for c in role_claims])
        return claims

    async def fetch_all_claims_role(self, role: discord.Role):
        async with aiosqlite.connect(self.resolved_db_path) as db:
            async with db.execute(
                    """
                    SELECT claimName FROM ClaimsMapping
                    WHERE fk_roleId = ?
                    """, (role.id,)) as c:
                claims = await self.fetcthall_as_dict(c)
                if len(claims) == 0:
                    return
                return [c['claimName'] for c in claims]

    async def add_claim_mapping(self, claim: str, role: discord.Role):
        async with aiosqlite.connect(self.resolved_db_path) as db:
            await db.execute(
                """
                INSERT INTO ClaimsMapping (claimName, fk_roleId, fk_guildId)
                VALUES (?, ?, ?)
                """, (claim, role.id, role.guild.id))
            await db.commit()

    async def remove_claim_mapping(self, claim: str, role: discord.Role):
        async with aiosqlite.connect(self.resolved_db_path) as db:
            await db.execute(
                """
                DELETE FROM ClaimsMapping 
                WHERE claimName = ? and fk_roleId = ?
                """, (claim, role.id))
            await db.commit()

    async def check_claim_role(self, claim: Claims, role: discord.Role) -> bool:
        async with aiosqlite.connect(self.resolved_db_path) as db:
            async with db.execute('SELECT * FROM ClaimsMapping WHERE claimName = ? and fk_roleId = ?', (claim.name, role.id)) as c:
                return await c.fetchone() is not None

    async def check_claim_user(self, claim: Claims, user: discord.User) -> bool:
        return claim.name in await self.fetch_all_claims_user(user)
