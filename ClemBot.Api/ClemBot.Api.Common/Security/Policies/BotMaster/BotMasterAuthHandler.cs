using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Http;
using Microsoft.Extensions.Logging;

namespace ClemBot.Api.Common.Security.Policies.BotMaster;

public class BotMasterAuthHandler : AuthorizationHandler<BotMasterRequirement>
{
    private readonly ILogger<BotMasterAuthHandler> _logger;
    private readonly HttpContext? _requestContext;

    public BotMasterAuthHandler(ILogger<BotMasterAuthHandler> logger, IHttpContextAccessor requestContext)
    {
        _logger = logger;
        _requestContext = requestContext.HttpContext;
    }

    protected override Task HandleRequirementAsync(AuthorizationHandlerContext context,
        BotMasterRequirement requirement)
    {
        if (context.User.HasClaim(c => c.Type == Claims.BotApiKey))
        {
            context.Succeed(requirement);
        }

        return Task.CompletedTask;
    }
}
