using System.Collections.Generic;
using System.Security.Claims;
using System.Threading;
using System.Threading.Tasks;
using ClemBot.Api.Core.Features.Roles.Bot;
using ClemBot.Api.Core.Security.JwtToken;
using ClemBot.Api.Core.Security.OAuth;
using ClemBot.Api.Core.Utilities;
using ClemBot.Api.Data.Contexts;
using ClemBot.Api.Data.Extensions;
using MediatR;
using Microsoft.AspNetCore.Http;
using Microsoft.Extensions.Logging;

namespace ClemBot.Api.Core.Features.Authorization
{
    public class GetSiteUser
    {
        public class Query : IRequest<Result<Model, AuthorizeStatus>>
        {
        }

        public class Model
        {

        }

        public class Handler : IRequestHandler<Query, Result<Model, AuthorizeStatus>>
        {
            private readonly ClemBotContext _context;

            private readonly ILogger<BotAuthorize> _logger;

            private readonly IHttpContextAccessor _httpContextAccessor;

            private readonly IJwtAuthManager _jwtAuthManager;

            private readonly JwtTokenConfig _jwtTokenConfig;

            private readonly IDiscordAuthManager _discordAuthManager;

            public Handler(ClemBotContext context,
                ILogger<BotAuthorize> logger,
                IHttpContextAccessor httpContextAccessor,
                IJwtAuthManager jwtAuthManager,
                JwtTokenConfig jwtTokenConfig,
                IDiscordAuthManager discordAuthManager)
            {
                _context = context;
                _logger = logger;
                _httpContextAccessor = httpContextAccessor;
                _jwtAuthManager = jwtAuthManager;
                _jwtTokenConfig = jwtTokenConfig;
                _discordAuthManager = discordAuthManager;
            }

            public async Task<Result<Model, AuthorizeStatus>> Handle(Query request, CancellationToken cancellationToken)
            {
                var bar = await _context.Users.GetUserClaimsAsync(703008870338920470, 190858129188192257);

                _httpContextAccessor.HttpContext!.Request.Headers.TryGetValue("Origin", out var origin);
                _logger.LogInformation($"Site Login Request Initialized from Url: {origin}");
                if (!await _discordAuthManager.CheckTokenIsUserAsync(request.Bearer))
                {
                    _logger.LogInformation("Site Login Request Denied: Invalid Token");
                    return AuthorizeResult<Model>.Forbidden();
                }

                _logger.LogInformation("Site Login Request Accepted");

                var claims = new[]
                {
                    new Claim(Claims.DiscordBearer, request.Bearer),
                };

                return AuthorizeResult<Model>.Success();
            }
        }
    }
}
