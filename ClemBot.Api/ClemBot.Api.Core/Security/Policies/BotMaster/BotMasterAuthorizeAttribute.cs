using Microsoft.AspNetCore.Authorization;

namespace ClemBot.Api.Core.Security.Policies.BotMaster
{
    public class BotMasterAuthorizeAttribute : AuthorizeAttribute
    {
        public BotMasterAuthorizeAttribute()
        {
            Policy = Policies.BotMaster;
        }
    }
}
