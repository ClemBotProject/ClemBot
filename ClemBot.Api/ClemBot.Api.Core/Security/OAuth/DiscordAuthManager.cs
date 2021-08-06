using System.Net;
using System.Net.Http;
using System.Net.Http.Headers;
using System.Threading.Tasks;

namespace ClemBot.Api.Core.Security.OAuth
{
    public class DiscordAuthManager : IDiscordAuthManager
    {
        private readonly IHttpClientFactory _httpClientFactory;

        private const string DISCORD_USER_URL = @"https://discord.com/api/users/@me";

        public DiscordAuthManager(IHttpClientFactory httpClientFactory)
        {
            _httpClientFactory = httpClientFactory;
        }
        public async Task<bool> CheckToken(string bearer)
        {
            using var client = _httpClientFactory.CreateClient();
            client.DefaultRequestHeaders.Authorization = new AuthenticationHeaderValue("Bearer", bearer);

            var resp = await client.GetAsync(DISCORD_USER_URL);

            return resp.StatusCode == HttpStatusCode.OK;
        }
    }
}
