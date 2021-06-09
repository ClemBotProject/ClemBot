using System;
using System.Collections.Generic;
using System.Linq;
using ClemBot.Api.Data.Enums;

namespace ClemBot.Api.Core.Security.Policies.GuildSandbox
{
    public class GuildSandboxPolicyParser : IPolicyParser<IEnumerable<BotAuthClaims>>
    {
        public const string POLICY_PREFIX = Policies.GuildSandbox;

        /// <inheritdoc cref="IPolicyParser{T}.Serialize"/>
        public string Serialize(IEnumerable<BotAuthClaims>? t)
            => $"{POLICY_PREFIX}{string.Join(';', t ?? new List<BotAuthClaims>())}";

        /// <inheritdoc cref="IPolicyParser{T}.Deserialize"/>
        public IEnumerable<BotAuthClaims>? Deserialize(string val)
        {
            if (!val.StartsWith(POLICY_PREFIX))
            {
                return null;
            }

            var claimsStr = val.Substring(POLICY_PREFIX.Length);

            return string.IsNullOrEmpty(claimsStr)
                ? new List<BotAuthClaims>()
                : claimsStr.Split(';').Select(Enum.Parse<BotAuthClaims>);
        }
    }
}
