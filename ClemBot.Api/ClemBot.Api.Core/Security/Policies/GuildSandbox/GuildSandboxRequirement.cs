using Microsoft.AspNetCore.Authorization;

namespace ClemBot.Api.Core.Security.Policies.GuildSandbox
{
    /// <summary>
    /// Marker class to define a request that is sandboxed to a particular guild
    /// </summary>
    public class GuildSandboxRequirement : IAuthorizationRequirement
    {
    }
}
