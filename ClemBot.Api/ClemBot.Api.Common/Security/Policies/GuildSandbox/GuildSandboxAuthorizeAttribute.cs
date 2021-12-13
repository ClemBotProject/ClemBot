using ClemBot.Api.Common.Enums;

namespace ClemBot.Api.Common.Security.Policies.GuildSandbox;

public class GuildSandboxAuthorizeAttribute : Attribute //: AuthorizeAttribute
{
    private readonly GuildSandboxPolicyParser _parser = new();

    public IEnumerable<BotAuthClaims> Claims {get; set; }

    public GuildSandboxAuthorizeAttribute(params BotAuthClaims[] claims)
    {
        Claims = claims.ToList();
    }
}
