using System;
using System.Security.Claims;
using System.Threading;
using System.Threading.Tasks;
using ClemBot.Api.Common;
using ClemBot.Api.Common.Security;
using ClemBot.Api.Common.Security.JwtToken;
using ClemBot.Api.Common.Utilities;
using ClemBot.Api.Core.Behaviors;
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

    public record Query : IRequest<AuthorizeResult<Model>>
    {
        public string Key { get; set; } = null!;
    }

    public record Model : IResponseModel
    {
        public string Token { get; init; } = null!;
    }

    public class Handler : IRequestHandler<Query, AuthorizeResult<Model>>
    {
        private ILogger<Handler> _logger { get; init; }

        private IHttpContextAccessor _httpContextAccessor { get; init; }

        private IJwtAuthManager _jwtAuthManager { get; init; }

        private ApiKey _apiKey { get; init; }

        public Handler(ILogger<Handler> logger,
            IHttpContextAccessor httpContextAccessor,
            IJwtAuthManager jwtAuthManager,
            ApiKey apiKey)
        {
            _logger = logger;
            _httpContextAccessor = httpContextAccessor;
            _jwtAuthManager = jwtAuthManager;
            _apiKey = apiKey;
        }

        public Task<AuthorizeResult<Model>> Handle(Query request,
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
                new Claim(Claims.BotApiKey, "")
            };

            _logger.LogInformation("Generating JWT Access Token");
            var token = _jwtAuthManager.GenerateToken(claims, DateTime.UtcNow.AddDays(1));
            _logger.LogInformation("JWT Access Token Successfully Generated");

            return Task.FromResult(AuthorizeResult<Model>.Success(new Model() { Token = token }));
        }
    }
}
