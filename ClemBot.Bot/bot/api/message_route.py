import typing as t

from bot.api.api_client import ApiClient
from bot.api.base_route import BaseRoute


class MessageRoute(BaseRoute):

    def __init__(self, api_client: ApiClient):
        super().__init__(api_client)

    async def create_message(self,
                             message_id: int,
                             content: str,
                             guild_id: int,
                             author_id: int,
                             channel_id: int,
                             **kwargs):

        json = {'Messages': [{
            'Id': message_id,
            'Content': content,
            'GuildId': guild_id,
            'UserId': author_id,
            'ChannelId': channel_id
        }]}

        await self._client.post('bot/messages', data=json, **kwargs)

    async def batch_create_message(self, messages: t.Iterable, **kwargs):
        messages = [{
            'Id': m.id,
            'Content': m.content,
            'GuildId': m.guild,
            'UserId': m.author,
            'ChannelId': m.channel,
            'Time': m.time.strftime('%Y-%m-%dT%H:%M:%S.%f')
        } for m in messages]

        json = {'Messages': messages}

        await self._client.post('bot/messages', data=json, **kwargs)

    async def edit_message(self, message_id: int, content: str):
        json = {'Messages': [{
            'Id': message_id,
            'Content': content,
        }]}

        await self._client.patch('bot/messages', data=json)

    async def batch_edit_message(self, messages: t.Iterable, **kwargs):
        messages = [{
            'Id': m.id,
            'Content': m.content,
            'Time': m.time.strftime('%Y-%m-%dT%H:%M:%S.%f')
        } for m in messages]

        json = {'Messages': messages}
        await self._client.patch('bot/messages', data=json, **kwargs)

    async def get_message(self, message_id: int):
        return await self._client.get(f'bot/messages/{message_id}')

    async def range_count_messages(self, user_id: int, guild_id: int, days: int):
        json = {
            'UserId' : user_id,
            'GuildId' : guild_id,
            'Days' : days
        }
        resp = await self._client.get('bot/messages/Count', data=json)
        
        if not resp:
        	return 0
        	
        return resp['messageCount']
