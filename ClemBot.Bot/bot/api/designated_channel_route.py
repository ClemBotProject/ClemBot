from bot.api.api_client import ApiClient
from bot.api.base_route import BaseRoute


class DesignatedChannelRoute(BaseRoute):

    def __init__(self, api_client: ApiClient):
        super().__init__(api_client)

    async def register_channel(self,
                               channel_id: int,
                               designation: str,
                               **kwargs):
        json = {
            'ChannelId': channel_id,
            'Designation': designation
        }

        return await self._client.post('designatedchannels', data=json, **kwargs)

    async def delete_channel(self,
                             channel_id: int,
                             designation: str,
                             **kwargs):
        json = {
            'ChannelId': channel_id,
            'Designation': designation
        }

        return await self._client.delete('designatedchannels', data=json, **kwargs)

    async def get_guild_designated_channel_ids(self,
                                               guild_id: int,
                                               designation: str):
        json = {
            'GuildId': guild_id,
            'Designation': designation
        }
        resp = await self._client.get('designatedchannels/details', data=json)

        if not resp:
            return []

        return resp['mappings']

    async def get_guild_all_designated_channels(self, guild_id: int):
        resp = await self._client.get(f'guilds/{guild_id}/designatedchannels')

        if not resp:
            return {}

        return {i['designation']: i['channelIds'] for i in resp}

    async def get_global_designations(self, designation: str):
        return await self._client.get(f'designatedchannels/{designation}/index')
