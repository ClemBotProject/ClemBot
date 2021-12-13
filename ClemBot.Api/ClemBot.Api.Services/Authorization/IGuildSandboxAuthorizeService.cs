using System.Collections.Generic;
using System.Threading.Tasks;
using ClemBot.Api.Common.Enums;
using ClemBot.Api.Common.Security.Policies.GuildSandbox;

namespace ClemBot.Api.Services.Authorization;

public interface IGuildSandboxAuthorizeService
{
    Task<bool> AuthorizeUser(IGuildSandboxModel model);
}
