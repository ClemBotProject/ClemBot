import typing as t

from bot.api.api_client import ApiClient
from bot.api.base_route import BaseRoute


class ThreadRoute(BaseRoute):

    def __init__(self, api_client: ApiClient):
        super().__init__(api_client)

    async def create_thread(self,
                            thread_id: int,
                            name: int,
                            guild_id: int,
                            parent_id: int,
                            **kwargs):
        json = {
            'Id': thread_id,
            'Name': name,
            'GuildId': guild_id,
            'ParentId': parent_id
        }
        await self._client.post('bot/threads', data=json, **kwargs)

    async def get_thread(self, thread_id: int):
        return await self._client.get(f'bot/threads/{thread_id}')

    async def edit_thread(self, thread_id: int, name: str, **kwargs):
        json = {
            'Id': thread_id,
            'Name': name,
        }

        return await self._client.patch('bot/threads', data=json, **kwargs)

    async def remove_thread(self, thread_id: int, **kwargs):
        return await self._client.delete(f'bot/threads/{thread_id}', **kwargs)

    async def get_guilds_threads(self, guild_id: int) -> t.Optional[t.List[int]]:
        return await self._client.get(f'bot/guilds/{guild_id}/threads')
