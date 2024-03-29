import typing as t
from datetime import datetime

from bot.api.api_client import ApiClient
from bot.api.base_route import BaseRoute
from bot.consts import Infractions
from bot.models.moderation_models import Infraction


class ModerationRoute(BaseRoute):
    def __init__(self, api_client: ApiClient):
        super().__init__(api_client)

    async def insert_ban(
        self, *, guild_id: int, author_id: int, subject_id: int, reason: str | None, **kwargs: t.Any
    ) -> int | None:
        json = {
            "GuildId": guild_id,
            "AuthorId": author_id,
            "SubjectId": subject_id,
            "Reason": reason,
            "Type": Infractions.ban,
        }

        resp = await self._client.post("bot/infractions", data=json, **kwargs)

        if not resp:
            return None

        return t.cast(int, resp["infractionId"])

    async def insert_mute(
        self,
        *,
        guild_id: int,
        author_id: int,
        subject_id: int,
        reason: str | None = None,
        duration: str,
        **kwargs: t.Any,
    ) -> int | None:
        json = {
            "GuildId": guild_id,
            "AuthorId": author_id,
            "SubjectId": subject_id,
            "Reason": reason,
            "Duration": duration,
            "Type": Infractions.mute,
            "Active": True,
        }

        resp = await self._client.post("bot/infractions", data=json, **kwargs)

        if not resp:
            return None

        return t.cast(int, resp["infractionId"])

    async def insert_warn(
        self, *, guild_id: int, author_id: int, subject_id: int, reason: str, **kwargs: t.Any
    ) -> int | None:
        json = {
            "GuildId": guild_id,
            "AuthorId": author_id,
            "SubjectId": subject_id,
            "Reason": reason,
            "Type": Infractions.warn,
        }
        resp = await self._client.post("bot/infractions", data=json, **kwargs)

        if not resp:
            return None

        return t.cast(int, resp["infractionId"])

    async def delete_infraction(self, infraction_id: int, **kwargs: t.Any) -> int:
        return t.cast(int, await self._client.delete(f"bot/infractions/{infraction_id}", **kwargs))

    async def deactivate_mute(self, infraction_id: int, **kwargs: t.Any) -> int:
        return t.cast(
            int, await self._client.patch(f"bot/infractions/{infraction_id}/deactivate", **kwargs)
        )

    async def get_infraction(self, infraction_id: int) -> Infraction:
        dict = await self._client.get(f"bot/infractions/{infraction_id}")
        return Infraction(**dict)

    async def get_guild_infractions(self, guild_id: int) -> list[Infraction]:
        resp = await self._client.get(f"bot/guilds/{guild_id}/infractions")

        if not resp:
            return []

        return [Infraction(**i) for i in resp]

    async def get_guild_infractions_user(self, guild_id: int, user_id: int) -> list[Infraction]:
        resp = await self._client.get(f"bot/users/infractions/{user_id}/{guild_id}")

        if not resp:
            return []

        return [Infraction(**i) for i in resp]

    async def get_guild_warns_user(self, guild_id: int, user_id: int) -> list[Infraction]:
        resp = await self._client.get(f"bot/users/infractions/{user_id}/{guild_id}/warn")

        if not resp:
            return []

        return [Infraction(**i) for i in resp]

    async def get_guild_mutes_user(self, guild_id: int, user_id: int) -> list[Infraction]:
        resp = await self._client.get(f"bot/users/infractions/{user_id}/{guild_id}/mute")

        if not resp:
            return []

        return [Infraction(**i) for i in resp]

    async def get_guild_bans_user(self, guild_id: int, user_id: int) -> list[Infraction]:
        resp = await self._client.get(f"bot/users/infractions/{user_id}/{guild_id}/ban")

        if not resp:
            return []

        return [Infraction(**i) for i in resp]
