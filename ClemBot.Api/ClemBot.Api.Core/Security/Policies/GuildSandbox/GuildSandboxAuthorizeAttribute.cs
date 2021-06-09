using System.Collections.Generic;
using ClemBot.Api.Data.Enums;
using Microsoft.AspNetCore.Authorization;

namespace ClemBot.Api.Core.Security.Policies.GuildSandbox
{
    public class GuildSandboxAuthorizeAttribute : AuthorizeAttribute
    {
        private readonly GuildSandboxPolicyParser _parser = new();

        public IEnumerable<BotAuthClaims> Claims
        {
            get => _parser.Deserialize(Policy ?? "") ?? new List<BotAuthClaims>();
            init => Policy = _parser.Serialize(value);
        }

        public GuildSandboxAuthorizeAttribute(params BotAuthClaims[] claims)
        {
            Claims = claims;
        }

        public GuildSandboxAuthorizeAttribute()
        {
            Claims = new List<BotAuthClaims>();
        }
    }
}
