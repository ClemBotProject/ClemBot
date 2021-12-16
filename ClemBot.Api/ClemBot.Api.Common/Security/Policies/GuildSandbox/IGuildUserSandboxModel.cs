namespace ClemBot.Api.Common.Security.Policies.GuildSandbox;

public interface IGuildUserSandboxModel : IGuildSandboxModel
{
    /// <summary>
    /// Defines a UserId to check in a policy to ensure a request
    /// isn't escaping the bounds of its authorized user
    /// </summary>
    public ulong UserId { get; init; }
}
