using Microsoft.AspNetCore.Authorization;

namespace ClemBot.Api.Common.Security.Policies.GuildSandbox;

/// <summary>
/// Marker class to define a request that is sandboxed to a particular guild
/// </summary>
public class GuildSandboxRequirement : IAuthorizationRequirement
{
}
