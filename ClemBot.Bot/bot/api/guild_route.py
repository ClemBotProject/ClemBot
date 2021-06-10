import typing as t

import discord

from bot.api.api_client import ApiClient
from bot.api.base_route import BaseRoute


class GuildRoute(BaseRoute):

    def __init__(self, api_client: ApiClient):
        super().__init__(api_client)

    async def add_guild(self, guild_id: int, name: str):
        if await self._client.get(f'guilds/{guild_id}'):
            return

        json = {
            'Id': guild_id,
            'Name': name
        }
        await self._client.post('guilds', data=json)

    async def get_all_guilds_ids(self):
        guilds = await self._client.get('guilds')

        if not guilds:
            return

        return [g['id'] for g in guilds]

    async def leave_guild(self, guild_id: int):
        return await self._client.delete(f'guilds/{guild_id}')

    async def get_guild(self, guild_id: int):
        return await self._client.get(f'guilds/{guild_id}')

    async def get_guild_user_ids(self, guild_id: int):
        guild = await self._client.get(f'guilds/{guild_id}')

        if not guild:
            return

        return guild['users']

    async def edit_guild(self, guild_id: int, name: str):
        json = {
            'Id': guild_id,
            'Name': name,
        }

        await self._client.patch('guilds', data=json)

    async def update_guild_users(self, guilds: t.List[discord.Guild]):

        guilds = [{
            'GuildId': g.id,
            'Users': [{
                'UserId': u.id,
                'Name': u.name
            }
                for u in g.members]
        }
            for g in guilds]

        json = {
            'Guilds': guilds
        }

        await self._client.patch(f'guilds/update/users', data=json)

    async def update_guild_roles(self, guilds: t.List[discord.Guild]):
        guilds = [{
            'GuildId': g.id,
            'Roles': [{
                'Id': r.id,
                'Name': r.name,
                'Admin': r.permissions.administrator,
                'Members': [
                    m.id for m in r.members
                ]
            }
                for r in g.roles]
        }
            for g in guilds]

        json = {
            'Guilds': guilds
        }

        await self._client.patch(f'guilds/update/roles', data=json)

    async def update_guild_channels(self, guilds: t.List[discord.Guild]):

        guilds = [{
            'GuildId': g.id,
            'Channels': [{
                'ChannelId': c.id,
                'Name': c.name
            }
                for c in g.channels]
        }
            for g in guilds]

        json = {
            'Guilds': guilds
        }
        await self._client.patch(f'guilds/update/channels', data=json)
