namespace ClemBot.Api.Common.Security.Policies.GuildSandbox;

public interface IGuildSandboxModel
{
    /// <summary>
    /// Defines a GuildId to check in a policy to ensure a request
    /// isn't escaping the bounds of its authorized guild
    /// </summary>
    ulong GuildId { get; init; }
}
