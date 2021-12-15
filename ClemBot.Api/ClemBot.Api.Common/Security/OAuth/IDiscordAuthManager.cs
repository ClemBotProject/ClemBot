using ClemBot.Api.Common.Security.OAuth.OAuthUser;

namespace ClemBot.Api.Common.Security.OAuth
{
    public interface IDiscordAuthManager
    {
        Task<bool> CheckTokenIsUserAsync(string bearer);
        Task<DiscordOAuthModel?> GetDiscordUserAsync(string bearer);
        Task<List<Guild>?> GetDiscordUserGuildsAsync(string bearer);
    }
}
