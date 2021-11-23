using System.Security.Claims;
using System.Text.Json;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Http;

namespace ClemBot.Api.Core.Security.Policies.GuildSandbox;

public class GuildSandboxAuthHandler : AuthorizationHandler<GuildSandboxRequirement>
{
    private readonly ILogger<GuildSandboxAuthHandler> _logger;
    private readonly HttpContext? _requestContext;

    public GuildSandboxAuthHandler(ILogger<GuildSandboxAuthHandler> logger, IHttpContextAccessor requestContext)
    {
        _logger = logger;
        _requestContext = requestContext.HttpContext;
    }

    protected override async Task HandleRequirementAsync(AuthorizationHandlerContext context,
        GuildSandboxRequirement requirement)
    {
        _logger.LogInformation("Auth Handler {This} received request", GetType());
        if (context.User.HasClaim(c => c.Type == Claims.BotApiKey))
        {
            _logger.LogInformation("Auth Handler {This} received Bot request", GetType());
            context.Succeed(requirement);
            return;
        }

        var req = _requestContext?.Request;

        if (req is null)
        {
            _logger.LogInformation("Handler {This} received null Http request", GetType());
            return;
        }

        _logger.LogInformation("Enabling Model Buffering in Auth Handler {This}", GetType());
        req.EnableBuffering();

        var model = await JsonSerializer.DeserializeAsync<GuildSandboxModel>(req.Body);

        if (model is null)
        {
            _logger.LogError("Auth Handler {This} received invalid Http Request Body " +
                             "(Does your command inherit from {Model}", GetType(), typeof(GuildSandboxModel));
            return;
        }

        if (!ulong.TryParse(context.User.FindFirstValue(Claims.ContextGuildId), out var activeGuildId))
        {
            _logger.LogError("Auth Handler {This} received invalid GuildId value, Value was: {Model}", GetType(), Claims.ContextGuildId);
            return;
        }

        if (activeGuildId != model.GuildId)
        {
            _logger.LogInformation("Auth Handler {This} failed requirements", GetType());
            return;
        }

        _logger.LogInformation("Auth Handler {This} Accepted requirements", GetType());
        context.Succeed(requirement);

        req.Body.Position = 0;
    }
}
