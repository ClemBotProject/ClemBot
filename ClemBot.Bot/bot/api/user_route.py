import typing as t

import discord

from bot.api.api_client import ApiClient
from bot.api.base_route import BaseRoute
import bot.models.user_models as models
from bot.models.reminder_models import Reminder


class UserRoute(BaseRoute):
    def __init__(self, api_client: ApiClient):
        super().__init__(api_client)

    async def create_user(self, user_id: int, name: str, **kwargs: t.Any) -> None:
        json = {
            "Id": user_id,
            "Name": name,
        }
        await self._client.post("bot/users", data=json, **kwargs)

    async def create_user_bulk(self, users: t.Iterable[discord.User], **kwargs: t.Any) -> None:
        json = {
            "Users": [
                {
                    "Id": u.id,
                    "Name": u.name,
                }
                for u in users
            ]
        }

        await self._client.post("bot/users/createbulk", data=json, **kwargs)

    async def get_user(self, user_id: int) -> models.User:
        return models.User(**await self._client.get(f"bot/users/{user_id}"))

    async def get_user_slot_scores(
        self, user_id: int, guild_id: int, limit: int
    ) -> models.UserSlotScores | None:
        resp = await self._client.get(f"bot/users/{user_id}/{guild_id}/slotscores?limit={limit}")

        if not resp:
            return None

        return models.UserSlotScores(**resp)

    async def add_user_guild(self, user_id: int, guild_id: int, **kwargs: t.Any) -> None:
        json = {
            "GuildId": guild_id,
            "UserId": user_id,
        }
        await self._client.post("bot/guilds/adduser", data=json, **kwargs)

    async def remove_user_guild(self, user_id: int, guild_id: int, **kwargs: t.Any) -> None:
        json = {
            "GuildId": guild_id,
            "UserId": user_id,
        }
        await self._client.delete("bot/guilds/removeuser", data=json, **kwargs)

    async def get_user_guilds_ids(self, user_id: int) -> list[int] | None:
        user = await self._client.get(f"bot/users/{user_id}")

        if not user:
            return None

        return [g.id for g in user.value["Guilds"]]

    async def edit_user(self, user_id: int, name: str) -> None:
        json = {
            "Id": user_id,
            "Name": name,
        }

        await self._client.patch("bot/users/edit", data=json)

    async def get_users_ids(self) -> list[int]:
        users = await self._client.get("users")

        if not users:
            return []

        return [u["id"] for u in users]

    async def update_roles(self, user_id: int, roles: t.Iterable[int], **kwargs: t.Any) -> None:
        json = {"Roles": roles}

        await self._client.post(f"bot/users/{user_id}/updateroles", data=json, **kwargs)

    async def get_reminders(self, user_id: int, **kwargs: t.Any) -> list[Reminder]:
        resp = await self._client.get(f"bot/users/{user_id}/reminders", **kwargs)

        if not resp:
            return []

        return [Reminder(**i) for i in resp]
