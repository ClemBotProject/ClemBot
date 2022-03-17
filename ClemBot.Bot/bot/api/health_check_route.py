
from bot.api.api_client import ApiClient
from bot.api.base_route import BaseRoute


class HealthCheckRoute(BaseRoute):
    def __init__(self, api_client: ApiClient):
        super().__init__(api_client)
        
    async def ping(self):
        return await self._client.get("HealthCheck/ping")
