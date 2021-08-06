using System.Threading.Tasks;

namespace ClemBot.Api.Core.Security.OAuth
{
    public interface IDiscordAuthManager
    {
        Task<bool> CheckToken(string bearer);
    }
}
