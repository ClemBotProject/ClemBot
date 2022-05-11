import typing as t

import discord
import pandas as pd

from bot.api.api_client import ApiClient
from bot.api.base_route import BaseRoute
from bot.consts import GuildSettings


class GuildRoute(BaseRoute):

    def __init__(self, api_client: ApiClient):
        super().__init__(api_client)

    async def add_guild(self, guild_id: int, name: str, owner_id):
        if await self._client.get(f'bot/guilds/{guild_id}'):
            return

        json = {
            'Id': guild_id,
            'Name': name,
            'OwnerId': owner_id
        }
        await self._client.post('bot/guilds', data=json)

    async def get_all_guilds_ids(self):
        guilds = await self._client.get('bot/guilds')

        if not guilds:
            return

        return [g['id'] for g in guilds]

    async def leave_guild(self, guild_id: int):
        return await self._client.delete(f'bot/guilds/{guild_id}')

    async def get_guild(self, guild_id: int):
        return await self._client.get(f'bot/guilds/{guild_id}')

    async def get_all_guilds(self):
        return await self._client.get(f'bot/guilds')

    async def get_guild_slot_scores(self, guild_id: int, limit: int, leader: bool):
        resp = await self._client.get(f'bot/Guilds/{guild_id}/SlotScores', params={'leader': str(leader), 'limit': limit})
        return resp['scores']

    async def get_guild_user_ids(self, guild_id: int):
        guild = await self._client.get(f'bot/guilds/{guild_id}')

        if not guild:
            return

        return guild['users']

    async def edit_guild(self, guild_id: int, name: str, owner_id: int):
        json = {
            'Id': guild_id,
            'Name': name,
            'OwnerId': owner_id
        }

        await self._client.patch('bot/guilds', data=json)

    async def update_guild_users(self, guild: discord.Guild):

        users = [{
                'UserId': u.id,
                'Name': u.name
            }
                for u in guild.members]

        df: pd.DataFrame = pd.DataFrame.from_records(users)

        json = {
            'GuildId': guild.id,
            'UserCsv': df.to_csv(index=False)
        }

        await self._client.patch(f'bot/guilds/update/users', data=json)

    async def update_guild_roles(self, guild: discord.Guild):
        roles = [{
                'Id': r.id,
                'Name': r.name,
                'Admin': r.permissions.administrator,
            }
                for r in guild.roles]

        df: pd.DataFrame = pd.DataFrame.from_records(roles)

        json = {
            'GuildId': guild.id,
            'RoleCsv': df.to_csv(index=False)
        }

        await self._client.patch(f'bot/guilds/update/roles', data=json)

    async def update_guild_role_user_mappings(self, guild: discord.Guild):

        mappings = []
        for role in guild.roles:
            for user in role.members:
                mappings.append({'RoleId': role.id, 'UserId': user.id})

        df: pd.DataFrame = pd.DataFrame.from_records(mappings)

        json = {
            'GuildId': guild.id,
            'RoleMappingCsv': df.to_csv(index=False)
        }

        await self._client.patch(f'bot/guilds/update/RoleUserMappings', data=json)

    async def update_guild_channels(self, guild: discord.Guild):

        channels = [{
                'ChannelId': c.id,
                'Name': c.name
            }
                for c in guild.channels]

        df: pd.DataFrame = pd.DataFrame.from_records(channels)

        json = {
            'GuildId': guild.id,
            'ChannelCsv': df.to_csv(index=False)
        }

        await self._client.patch(f'bot/guilds/update/channels', data=json)

    async def update_guild_threads(self, guild: discord.Guild):

        threads = [{
            'ThreadId': c.id,
            'Name': c.name,
            'ParentId': c.parent_id
        }
            for c in guild.threads]

        df: pd.DataFrame = pd.DataFrame.from_records(threads)

        json = {
            'GuildId': guild.id,
            'ThreadCsv': df.to_csv(index=False)
        }

        await self._client.patch(f'bot/guilds/update/threads', data=json)

    async def get_can_embed_link(self, guild_id: int):
        resp = await self._client.get(f'guildsettings/{guild_id}/{GuildSettings.allow_embed_links.name}')
        return resp['value']

