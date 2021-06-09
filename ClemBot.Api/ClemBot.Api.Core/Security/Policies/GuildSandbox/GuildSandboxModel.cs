namespace ClemBot.Api.Core.Security.Policies.GuildSandbox
{
    public record GuildSandboxModel : IGuildSandboxModel
    {
        public ulong GuildId { get; init; }

        public GuildSandboxModel()
        {
        }
    }
}
