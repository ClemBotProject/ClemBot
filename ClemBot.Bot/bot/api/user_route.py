import typing as t
import discord

from bot.api.api_client import ApiClient
from bot.api.base_route import BaseRoute


class UserRoute(BaseRoute):

    def __init__(self, api_client: ApiClient):
        super().__init__(api_client)

    async def create_user(self, user_id: int, name: str, **kwargs):
        json = {
            'Id': user_id,
            'Name': name,
        }
        await self._client.post('bot/users', data=json, **kwargs)

    async def create_user_bulk(self, users: t.Iterable[discord.User], **kwargs):
        users = [{
            'Id': u.id,
            'Name': u.name,
        }
            for u in users]

        json = {
            'Users': users
        }

        await self._client.post('bot/users/createbulk', data=json, **kwargs)

    async def get_user(self, user_id: int):
        return await self._client.get(f'bot/users/{user_id}')

    async def get_user_slot_scores(self, user_id: int, guild_id: int, limit: int):
        return await self._client.get(f'bot/users/{user_id}/{guild_id}/slotscores?limit={limit}')

    async def add_user_guild(self, user_id: int, guild_id: int, **kwargs):
        json = {
            'GuildId': guild_id,
            'UserId': user_id,
        }
        await self._client.post('bot/guilds/adduser', data=json, **kwargs)

    async def remove_user_guild(self, user_id: int, guild_id: int, **kwargs):
        json = {
            'GuildId': guild_id,
            'UserId': user_id,
        }
        await self._client.delete('bot/guilds/removeuser', data=json, **kwargs)

    async def get_user_guilds_ids(self, user_id: int):
        user = await self._client.get(f'bot/users/{user_id}')

        if not user:
            return

        return [g.id for g in user.value['Guilds']]

    async def edit_user(self, user_id: int, name: str):
        json = {
            'Id': user_id,
            'Name': name,
        }

        await self._client.patch('bot/users/edit', data=json)

    async def get_users_ids(self) -> t.Optional[t.List[int]]:
        users = await self._client.get(f'users')

        if not users:
            return []

        return [u['id'] for u in users]

    async def update_roles(self, user_id: int, roles: t.Iterable[int], **kwargs):
        json = {
            'Roles': roles
        }

        await self._client.post(f'bot/users/{user_id}/updateroles', data=json, **kwargs)
