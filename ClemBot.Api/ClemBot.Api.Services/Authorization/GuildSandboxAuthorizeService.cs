using System;
using System.Collections.Generic;
using System.Linq;
using System.Security.Claims;
using System.Threading.Tasks;
using ClemBot.Api.Common;
using ClemBot.Api.Common.Enums;
using ClemBot.Api.Common.Security.Policies.GuildSandbox;
using ClemBot.Api.Data.Contexts;
using ClemBot.Api.Data.Models;
using Microsoft.AspNetCore.Mvc;
using Microsoft.AspNetCore.Mvc.Infrastructure;
using Microsoft.Extensions.Logging;

namespace ClemBot.Api.Services.Authorization;

public class GuildSandboxAuthorizeService : IGuildSandboxAuthorizeService
{
    private readonly ActionContext _contextAccessor;

    private readonly ILogger<GuildSandboxAuthorizeService> _logger;

    private readonly ClaimsPrincipal User;

    private readonly ClemBotContext _context;

    public GuildSandboxAuthorizeService(IActionContextAccessor contextAccessor,
        ILogger<GuildSandboxAuthorizeService> logger,
        ClemBotContext context)
    {
        _logger = logger;
        _context = context;
        _contextAccessor = contextAccessor.ActionContext ?? throw new ArgumentNullException(nameof(contextAccessor));
        User = _contextAccessor.HttpContext.User;
    }

    public async Task<bool> AuthorizeUser(IGuildSandboxModel model)
    {
        _logger.LogInformation("Auth Handler: {This} received request", GetType());
        if (User.HasClaim(c => c.Type == Claims.BotApiKey))
        {
            _logger.LogInformation("Auth Handler: {This} received Bot request", GetType());
            return true;
        }

        var allowedClaims = _contextAccessor.ActionDescriptor.EndpointMetadata
            .OfType<GuildSandboxAuthorizeAttribute>()
            .FirstOrDefault()?.Claims;

        var userGuilds = await _context.Where(x => x.UserId == model.GuildId);

        User.FindFirst(Claims.)



        return true;

    }
}
