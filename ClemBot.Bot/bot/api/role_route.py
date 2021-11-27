import typing as t

from bot.api.api_client import ApiClient
from bot.api.base_route import BaseRoute


class RoleRoute(BaseRoute):

    def __init__(self, api_client: ApiClient):
        super().__init__(api_client)

    async def create_role(self, role_id: int, name: int, is_admin: bool, guild_id: int, **kwargs):
        json = {
            'Id': role_id,
            'Name': name,
            'Admin': is_admin,
            'GuildId': guild_id
        }
        await self._client.post('bot/roles', data=json, **kwargs)

    async def get_role(self, role_id: int):
        return await self._client.get(f'bot/roles/{role_id}')

    async def edit_role(self, role_id: int, name: str, is_admin: bool, **kwargs):
        json = {
            'Id': role_id,
            'Name': name,
            'Admin': is_admin
        }

        await self._client.patch('bot/roles', data=json, **kwargs)

    async def set_assignable(self, role_id: int, assignable: bool, **kwargs):
        json = {
            'Id': role_id,
            'Assignable': assignable
        }

        await self._client.patch('bot/roles', data=json, **kwargs)

    async def remove_role(self, role_id: int, **kwargs):
        await self._client.delete(f'bot/roles/{role_id}', **kwargs)

    async def get_guilds_roles(self, guild_id: int) -> t.Optional[t.List[int]]:
        return await self._client.get(f'bot/guilds/{guild_id}/roles')

    async def get_guilds_assignable_roles(self, guild_id: int) -> t.Optional[t.List]:
        roles = await self._client.get(f'bot/guilds/{guild_id}/roles')

        if not roles:
            return

        return [r for r in roles if r['isAssignable']]

    async def check_role_assignable(self, role_id: int):
        roles = await self._client.get(f'bot/roles/{role_id}')

        if not roles:
            return

        return roles['isAssignable']
