using System.Threading.Tasks;
using ClemBot.Api.Core.Security.OAuth.OAuthUser;

namespace ClemBot.Api.Core.Security.OAuth
{
    public interface IDiscordAuthManager
    {
        Task<bool> CheckTokenIsUserAsync(string bearer);
        Task<DiscordOAuthModel?> GetDiscordUserAsync(string bearer);
    }
}
