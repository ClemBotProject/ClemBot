using Microsoft.AspNetCore.Authentication.JwtBearer;
using Microsoft.AspNetCore.Authorization;
using Microsoft.Extensions.Options;

namespace ClemBot.Api.Common.Security.Policies.GuildSandbox;

public class GuildSandboxPolicyProvider : IAuthorizationPolicyProvider
{
    private readonly GuildSandboxPolicyParser _parser = new();

    private readonly DefaultAuthorizationPolicyProvider _backupPolicyProvider;


    public GuildSandboxPolicyProvider(IOptions<AuthorizationOptions> options)
    {
        _backupPolicyProvider = new DefaultAuthorizationPolicyProvider(options);
    }

    public async Task<AuthorizationPolicy?> GetPolicyAsync(string policyName)
    {
        var claims = _parser.Deserialize(policyName);

        if (claims is null)
        {
            return await _backupPolicyProvider.GetPolicyAsync(policyName);
        }

        var policy = new AuthorizationPolicyBuilder();
        policy.Requirements.Add(new GuildSandboxRequirement());
        foreach (var claim in claims)
        {
            policy.RequireClaim(claim.ToString());
        }

        return policy.Build();
    }

    public Task<AuthorizationPolicy> GetDefaultPolicyAsync()
        => Task.FromResult(new AuthorizationPolicyBuilder(JwtBearerDefaults.AuthenticationScheme)
            .RequireAuthenticatedUser()
            .Build());

    public Task<AuthorizationPolicy?> GetFallbackPolicyAsync()
        => Task.FromResult<AuthorizationPolicy?>(null);
}
