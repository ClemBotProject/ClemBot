from bot.api.api_client import ApiClient
from bot.api.base_route import BaseRoute


class SlotsScoreRoute(BaseRoute):

    def __init__(self, api_client: ApiClient):
        super().__init__(api_client)

    async def add_slot_score(self,
                             score: int,
                             guild_id: int,
                             user_id: int,
                             **kwargs) -> None:
        json = {
            'Score': score,
            'GuildId': guild_id,
            'UserId': user_id
        }

        return await self._client.post('bot/slotscores', data=json, **kwargs)
