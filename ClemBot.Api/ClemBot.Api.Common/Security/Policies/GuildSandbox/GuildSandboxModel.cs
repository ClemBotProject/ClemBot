namespace ClemBot.Api.Common.Security.Policies.GuildSandbox;

public record GuildSandboxModel : IGuildSandboxModel
{
    public ulong GuildId { get; init; }

    public GuildSandboxModel()
    {
    }
}
