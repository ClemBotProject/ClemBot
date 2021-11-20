using System;
using System.Security.Claims;
using System.Threading;
using System.Threading.Tasks;
using ClemBot.Api.Core.Security;
using ClemBot.Api.Core.Security.JwtToken;
using ClemBot.Api.Core.Utilities;
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

    public class Query : IRequest<Result<Model, AuthorizeStatus>>
    {
        public string Key { get; set; } = null!;
    }

    public class Model
    {
        public string Token { get; set; } = null!;
    }

    public class Handler : IRequestHandler<Query, Result<Model, AuthorizeStatus>>
    {

        private readonly ClemBotContext _context;

        private readonly ILogger _logger;

        private readonly IHttpContextAccessor _httpContextAccessor;

        private readonly IJwtAuthManager _jwtAuthManager;

        private readonly JwtTokenConfig _jwtTokenConfig;

        private readonly ApiKey _apiKey;

        public Handler(ClemBotContext context,
            ILogger logger,
            IHttpContextAccessor httpContextAccessor,
            IJwtAuthManager jwtAuthManager,
            JwtTokenConfig jwtTokenConfig,
            ApiKey apiKey)
        {
            _context = context;
            _logger = logger;
            _httpContextAccessor = httpContextAccessor;
            _jwtAuthManager = jwtAuthManager;
            _jwtTokenConfig = jwtTokenConfig;
            _apiKey = apiKey;
        }

        public Task<Result<Model, AuthorizeStatus>> Handle(Query request,
            CancellationToken cancellationToken)
        {
            _httpContextAccessor.HttpContext!.Request.Headers.TryGetValue("Origin", out var origin);
            _logger.Information("Bot Authorize Request Initialized from Url: {Origin}", origin.ToString());
            if (request.Key != _apiKey.Key)
            {
                _logger.Information("Bot Authorize Request Denied: Invalid Key");
                return Task.FromResult(AuthorizeResult<Model>.Forbidden());
            }

            _logger.Information("Bot Authorize Request Accepted");

            _logger.Information("Generating Claim: {BotApiKey}", Claims.BotApiKey);
            var claims = new[]
            {
                new Claim(Claims.BotApiKey, request.Key)
            };

            _logger.Information("Generating JWT Access Token");
            var token = _jwtAuthManager.GenerateToken(claims, DateTime.Now);
            _logger.Information("JWT Access Token Successfully Generated");

            return Task.FromResult(AuthorizeResult<Model>.Success(new Model() { Token = token }));
        }
    }
}
