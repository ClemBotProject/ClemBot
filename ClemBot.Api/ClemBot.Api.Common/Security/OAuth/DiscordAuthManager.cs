using System.Net;
using System.Net.Http.Headers;
using System.Net.Http.Json;
using System.Text.Json;
using System.Text.Json.Serialization;
using ClemBot.Api.Common.Security.OAuth.OAuthUser;
using Microsoft.Extensions.Logging;

namespace ClemBot.Api.Common.Security.OAuth
{
    public class DiscordAuthManager : IDiscordAuthManager
    {
        private readonly IHttpClientFactory _httpClientFactory;

        private readonly ILogger<DiscordAuthManager> _logger;

        private const string DISCORD_USER_URL = @"https://discord.com/api/oauth2/@me";

        private const string DISCORD_USER_GUILDS_URL = @"https://discord.com/api/users/@me/guilds";

        public DiscordAuthManager(IHttpClientFactory httpClientFactory, ILogger<DiscordAuthManager> logger)
        {
            _httpClientFactory = httpClientFactory;
            _logger = logger;
        }
        public async Task<bool> CheckTokenIsUserAsync(string bearer)
        {
            using var client = _httpClientFactory.CreateClient();
            client.DefaultRequestHeaders.Authorization = new AuthenticationHeaderValue("Bearer", bearer);

            var resp = await client.GetAsync(DISCORD_USER_URL);

            return resp.StatusCode == HttpStatusCode.OK;
        }

        public async Task<DiscordOAuthModel?> GetDiscordUserAsync(string bearer)
        {
            using var client = _httpClientFactory.CreateClient();
            client.DefaultRequestHeaders.Authorization = new AuthenticationHeaderValue("Bearer", bearer);

            var resp = await client.GetAsync(DISCORD_USER_URL);

            return await resp.Content.ReadFromJsonAsync<DiscordOAuthModel>();
        }

        public async Task<List<Guild>?> GetDiscordUserGuildsAsync(string bearer)
        {
            using var client = _httpClientFactory.CreateClient();
            client.DefaultRequestHeaders.Authorization = new AuthenticationHeaderValue("Bearer", bearer);

            var resp = await client.GetAsync(DISCORD_USER_GUILDS_URL);

            if (resp.StatusCode != HttpStatusCode.OK)
            {
                _logger.LogError("Retrieving Users Guilds failed with status code {Code}", resp.StatusCode);
                return null;
            }

            return await resp.Content.ReadFromJsonAsync<List<Guild>>();
        }
    }
}
