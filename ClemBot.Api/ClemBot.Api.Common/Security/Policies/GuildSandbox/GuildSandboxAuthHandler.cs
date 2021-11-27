using System.Text.Json;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Http;
using Microsoft.Extensions.Logging;

namespace ClemBot.Api.Common.Security.Policies.GuildSandbox;

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

        IGuildSandboxModel? model;

        if (req.Query.TryGetValue("guildId", out var strid))
        {
            if (!ulong.TryParse(strid, out var id))
            {
                _logger.LogError("Auth Handler {This} received invalid GuildId query value, Value was: {Id}", GetType(), strid);
                return;
            }
            model = new GuildSandboxModel {GuildId = id};
        }
        else
        {
            model = await JsonSerializer.DeserializeAsync<GuildSandboxModel>(req.Body);
        }


        if (model is null)
        {
            _logger.LogError("Auth Handler {This} received invalid Http Request Body or invalid GuildId query param " +
                             "(Does your command inherit from {Model}", GetType(), typeof(GuildSandboxModel));
            return;
        }

        /*
        var claim = context.User.FindFirstValue(Claims.ContextGuildId);
        var guilds = JsonSerializer.Deserialize<List<string>>(claim);
        if (guilds is null)
        {
            _logger.LogError("Auth Handler {This} received invalid Claim GuildId value, Value was: {Model}", GetType(), Claims.ContextGuildId);
            return;
        }
        */

        /*
        if (!guilds.Contains(model.GuildId.ToString()))
        {
            _logger.LogError("Auth Handler {This} failed requirements", GetType());
            return;
        }
        */

        _logger.LogInformation("Auth Handler {This} Accepted requirements", GetType());
        context.Succeed(requirement);

        req.Body.Position = 0;
    }
}
