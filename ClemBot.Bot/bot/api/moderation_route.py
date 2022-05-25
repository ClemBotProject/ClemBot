import datetime
import typing as t

from bot.api.api_client import ApiClient
from bot.api.base_route import BaseRoute
from bot.consts import Infractions
from bot.models import Infraction


class ModerationRoute(BaseRoute):

    def __init__(self, api_client: ApiClient):
        super().__init__(api_client)

    async def insert_ban(self, *,
                         guild_id: int,
                         author_id: int,
                         subject_id: int,
                         reason: str,
                         **kwargs) -> t.Optional[int]:
        json = {
            'GuildId': guild_id,
            'AuthorId': author_id,
            'SubjectId': subject_id,
            'Reason': reason,
            'Type': Infractions.ban
        }

        resp = await self._client.post('bot/infractions', data=json, **kwargs)

        if not resp:
            return None

        return resp['infractionId']

    async def insert_mute(self, *,
                          guild_id: int,
                          author_id: int,
                          subject_id: int,
                          reason: t.Optional[str] = None,
                          duration: datetime,
                          **kwargs) -> t.Optional[int]:
        json = {
            'GuildId': guild_id,
            'AuthorId': author_id,
            'SubjectId': subject_id,
            'Reason': reason,
            'Duration': duration,
            'Type': Infractions.mute,
            'Active': True
        }

        resp = await self._client.post('bot/infractions', data=json, **kwargs)

        if not resp:
            return None

        return resp['infractionId']

    async def insert_warn(self, *,
                          guild_id: int,
                          author_id: int,
                          subject_id: int,
                          reason: str,
                          **kwargs) -> t.Optional[int]:
        json = {
            'GuildId': guild_id,
            'AuthorId': author_id,
            'SubjectId': subject_id,
            'Reason': reason,
            'Type': Infractions.warn
        }
        resp = await self._client.post('bot/infractions', data=json, **kwargs)

        if not resp:
            return None

        return resp['infractionId']

    async def delete_infraction(self, infraction_id: int, **kwargs) -> int:
        return await self._client.delete(f'bot/infractions/{infraction_id}', **kwargs)

    async def deactivate_mute(self, infraction_id: int, **kwargs) -> int:
        return await self._client.patch(f'bot/infractions/{infraction_id}/deactivate', **kwargs)

    async def get_infraction(self, infraction_id: int) -> t.Optional[Infraction]:
        return await self._client.get(f'bot/infractions/{infraction_id}')

    async def get_guild_infractions(self, guild_id: int) -> t.Iterator[Infraction]:
        resp = await self._client.get(f'bot/guilds/{guild_id}/infractions')

        if not resp:
            return []

        return [Infraction.from_dict(i) for i in resp]

    async def get_guild_infractions_user(self, guild_id: int, user_id: int) -> t.Iterator[Infraction]:
        resp = await self._client.get(f'bot/users/infractions/{user_id}/{guild_id}')

        if not resp:
            return []

        return [Infraction.from_dict(i) for i in resp]

    async def get_guild_warns_user(self, guild_id: int, user_id: int) -> t.Iterator[Infraction]:
        resp = await self._client.get(f'bot/users/infractions/{user_id}/{guild_id}/warn')

        if not resp:
            return []

        return [Infraction.from_dict(i) for i in resp]

    async def get_guild_mutes_user(self, guild_id: int, user_id: int) -> t.Iterator[Infraction]:
        resp = await self._client.get(f'bot/users/infractions/{user_id}/{guild_id}/mute')

        if not resp:
            return []

        return [Infraction.from_dict(i) for i in resp]

    async def get_guild_bans_user(self, guild_id: int, user_id: int) -> t.Iterator[Infraction]:
        resp = await self._client.get(f'bot/users/infractions/{user_id}/{guild_id}/ban')

        if not resp:
            return []

        return [Infraction.from_dict(i) for i in resp]
