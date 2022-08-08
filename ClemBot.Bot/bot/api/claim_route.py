import typing as t

import discord

from bot.api.api_client import ApiClient
from bot.api.base_route import BaseRoute
from bot.consts import Claims


class ClaimRoute(BaseRoute):
    def __init__(self, api_client: ApiClient):
        super().__init__(api_client)

    async def add_claim_mapping(self, claim: Claims, role_id: int, **kwargs: t.Any) -> None:
        json = {"RoleId": role_id, "Claim": claim.name}

        await self._client.post("bot/claimmappings", data=json, **kwargs)

    async def remove_claim_mapping(self, claim: Claims, role_id: int, **kwargs: t.Any) -> None:
        json = {"RoleId": role_id, "Claim": claim.name}

        await self._client.delete("bot/claimmappings", data=json, **kwargs)

    async def get_claims_role(self, role_id: int) -> list[Claims]:
        return [Claims[c] for c in await self._client.get(f"bot/roles/{role_id}/claimmappings")]

    async def get_claims_user(self, user: discord.Member) -> list[Claims]:
        return [
            Claims[c] for c in await self._client.get(f"bot/users/{user.id}/{user.guild.id}/claims")
        ]

    async def check_claim_role(self, claim: Claims, role: discord.Role) -> bool:
        return claim in await self.get_claims_role(role.id)

    async def check_claim_user(self, claim: Claims, user: discord.Member) -> bool:
        return claim in await self.get_claims_user(user)
