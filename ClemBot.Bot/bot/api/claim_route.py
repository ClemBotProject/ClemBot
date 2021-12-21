import discord

from bot.api.api_client import ApiClient
from bot.api.base_route import BaseRoute
from bot.consts import Claims


class ClaimRoute(BaseRoute):

    def __init__(self, api_client: ApiClient):
        super().__init__(api_client)

    async def add_claim_mapping(self, claim: Claims, role_id: int, **kwargs):
        json = {
            'RoleId': role_id,
            'Claim': claim
        }

        await self._client.post('bot/claimmappings', data=json, **kwargs)

    async def remove_claim_mapping(self, claim: Claims, role_id: int, **kwargs):
        json = {
            'RoleId': role_id,
            'Claim': claim
        }

        await self._client.delete('bot/claimmappings', data=json, **kwargs)

    async def get_claims_role(self, role_id):
        return await self._client.get(f'bot/roles/{role_id}/claimmappings')

    async def get_claims_user(self, user: discord.Member):
        resp = await self._client.get(f'bot/users/{user.id}/{user.guild.id}/claims')
        return resp

    async def check_claim_role(self, claim: Claims, role: discord.Role) -> bool:
        return claim.name in await self.get_claims_role(role.id)

    async def check_claim_user(self, claim: Claims, user: discord.Member) -> bool:
        return claim.name in await self.get_claims_user(user)
