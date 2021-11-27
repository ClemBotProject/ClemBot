using Microsoft.AspNetCore.Authorization;

namespace ClemBot.Api.Common.Security.Policies.BotMaster;

/// <summary>
/// Marker class to define a request that only the bot process is allowed to access
/// </summary>
public class BotMasterRequirement : IAuthorizationRequirement
{
}
