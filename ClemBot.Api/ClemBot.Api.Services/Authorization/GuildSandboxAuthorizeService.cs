using System;
using System.Collections.Generic;
using System.Linq;
using System.Security.Claims;
using System.Threading.Tasks;
using ClemBot.Api.Common;
using ClemBot.Api.Common.Enums;
using ClemBot.Api.Common.Security.Policies.GuildSandbox;
using ClemBot.Api.Data.Contexts;
using ClemBot.Api.Data.Extensions;
using ClemBot.Api.Data.Models;
using Microsoft.AspNetCore.Mvc;
using Microsoft.AspNetCore.Mvc.Infrastructure;
using Microsoft.EntityFrameworkCore;
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

        var claimId = User.FindFirst(Claims.DiscordUserId)?.Value;
        if (!ulong.TryParse(claimId, out var userId))
        {
           _logger.LogError("Invalid Claim: {Claim} found with value: {Value}", Claims.DiscordUserId, userId);
           return false;
        }

        var userGuilds = await _context.GuildUser
            .Where(x => x.UserId == userId)
            .Select(y => y.GuildId)
            .ToListAsync();

        var allowedClaims = _contextAccessor.ActionDescriptor.EndpointMetadata
            .OfType<GuildSandboxAuthorizeAttribute>()
            .FirstOrDefault()
            ?.Claims
            .ToList();

        if (allowedClaims is null)
        {
            _logger.LogError("Invalid Allowed Claims From token");
           return false;
        }

        if (model is IGuildUserSandboxModel userModel && userId != userModel.UserId)
        {
            _logger.LogError("Invalid request: {User} is does not match requested user {ReqUser}", userId, userModel.UserId);
            return false;
        }

        if (!userGuilds.Contains(model.GuildId))
        {
            _logger.LogError("Invalid request: {User} is not a member in {Guild}", userId, model.GuildId);
            return false;
        }

        var userClaims = await _context.Users.GetUserGuildClaimsAsync(model.GuildId, userId);
        if (allowedClaims.Any() && !userClaims.Intersect(allowedClaims).Any())
        {
            // User does not have correct claims
            _logger.LogError("Invalid request: {User} Does not have {Claims} in {Guild}", userId, allowedClaims, model.GuildId);
            return false;
        }

        _logger.LogInformation("Auth Request by user {User} in guild {Guild} accepted", userId, model.GuildId);
        return true;
    }
}
