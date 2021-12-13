using System;
using System.Security.Claims;
using System.Threading;
using System.Threading.Tasks;
using ClemBot.Api.Common;
using ClemBot.Api.Common.Security;
using ClemBot.Api.Common.Security.JwtToken;
using ClemBot.Api.Common.Utilities;
using ClemBot.Api.Core.Behaviors;
using ClemBot.Api.Data.Contexts;
using FluentValidation;
using MediatR;
using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Mvc;
using Serilog;

namespace ClemBot.Api.Core.Features.Authorization;

public class BotAuthorize
{
    public class Validator : AbstractValidator<Query>
    {
        public Validator()
        {
            RuleFor(p => p.Key).NotNull();
        }
    }

    public record Query : IRequest<IAuthorizeResult<Model>>
    {
        public string Key { get; set; } = null!;
    }

    public record Model : IResponseModel
    {
        public string Token { get; init; } = null!;
    }

    public record Handler(ClemBotContext _context,
        ILogger<Handler> _logger,
        IHttpContextAccessor _httpContextAccessor,
        IJwtAuthManager _jwtAuthManager,
        JwtTokenConfig _jwtTokenConfig,
        ApiKey _apiKey) : IRequestHandler<Query, IAuthorizeResult<Model>>
    {

        public Task<IAuthorizeResult<Model>> Handle(Query request,
            CancellationToken cancellationToken)
        {
            _httpContextAccessor.HttpContext!.Request.Headers.TryGetValue("Origin", out var origin);
            _logger.LogInformation("Bot Authorize Request Initialized from Url: {Origin}", origin.ToString());
            if (request.Key != _apiKey.Key)
            {
                _logger.LogInformation("Bot Authorize Request Denied: Invalid Key");
                return Task.FromResult(AuthorizeResult<Model>.Forbidden());
            }

            _logger.LogInformation("Bot Authorize Request Accepted");

            _logger.LogInformation("Generating Claim: {BotApiKey}", Claims.BotApiKey);
            var claims = new[]
            {
                new Claim(Claims.BotApiKey, request.Key)
            };

            _logger.LogInformation("Generating JWT Access Token");
            var token = _jwtAuthManager.GenerateToken(claims, DateTime.UtcNow.AddDays(1));
            _logger.LogInformation("JWT Access Token Successfully Generated");

            return Task.FromResult(AuthorizeResult<Model>.Success(new Model() { Token = token }));
        }
    }
}
