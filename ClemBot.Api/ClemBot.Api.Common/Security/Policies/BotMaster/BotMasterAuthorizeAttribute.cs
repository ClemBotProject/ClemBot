using Microsoft.AspNetCore.Authorization;

namespace ClemBot.Api.Common.Security.Policies.BotMaster;

public class BotMasterAuthorizeAttribute : AuthorizeAttribute
{
    public BotMasterAuthorizeAttribute()
    {
        Policy = Policies.BotMaster;
    }
}
