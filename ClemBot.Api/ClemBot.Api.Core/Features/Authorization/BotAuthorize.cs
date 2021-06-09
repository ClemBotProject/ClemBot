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
using Microsoft.Extensions.Logging;
using Serilog;

namespace ClemBot.Api.Core.Features.Authorization
{
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

        public record Handler(ClemBotContext _context,
                ILogger<BotAuthorize> _logger,
                IHttpContextAccessor _httpContextAccessor,
                IJwtAuthManager _jwtAuthManager,
                JwtTokenConfig _jwtTokenConfig,
                ApiKey _apiKey)
            : IRequestHandler<Query, Result<Model, AuthorizeStatus>>
        {
            public Task<Result<Model, AuthorizeStatus>> Handle(Query request,
                CancellationToken cancellationToken)
            {
                _httpContextAccessor.HttpContext!.Request.Headers.TryGetValue("Origin", out var origin);
                _logger.LogInformation($"Bot Authorize Request Initialized from Url: {origin.ToString()}");
                if (request.Key != _apiKey.Key)
                {
                    _logger.LogInformation("Bot Authorize Request Denied: Invalid Key");
                    return Task.FromResult(AuthorizeResult<Model>.Forbidden());
                }

                _logger.LogInformation("Bot Authorize Request Accepted");

                _logger.LogInformation($"Generating Claim: {Claims.BotApiKey}");
                var claims = new[]
                {
                    new Claim(Claims.BotApiKey, request.Key)
                };

                _logger.LogInformation("Generating JWT Access Token");
                var token = _jwtAuthManager.GenerateToken(claims, DateTime.Now);
                _logger.LogInformation("JWT Access Token Successfully Generated");

                return Task.FromResult(AuthorizeResult<Model>.Success(new Model() { Token = token }));
            }
        }
    }
}
