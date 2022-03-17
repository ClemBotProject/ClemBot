using ClemBot.Api.Common;
using ClemBot.Api.Common.Enums;
using ClemBot.Api.Common.Security.OAuth;
using ClemBot.Api.Common.Security.OAuth.OAuthUser;
using ClemBot.Api.Common.Utilities;
using ClemBot.Api.Data.Contexts;
using ClemBot.Api.Data.Extensions;
using Microsoft.AspNetCore.Http;
using Microsoft.EntityFrameworkCore;

namespace ClemBot.Api.Core.Features.Authorization;

public class GetSiteUser
{
    public class Query : IRequest<IAuthorizeResult<Model>>
    {
    }

    public class SiteUser
    {
        public DiscordOAuthModel User { get; set; } = null!;

        public List<Guild> Guilds { get; set; } = null!;
    }

    public class Model
    {
        public SiteUser User { get; set; } = null!;
    }

    public class Handler : IRequestHandler<Query, IAuthorizeResult<Model>>
    {
        private readonly ClemBotContext _context;

        private readonly ILogger<Handler> _logger;

        private readonly IHttpContextAccessor _httpContextAccessor;

        private readonly IDiscordAuthManager _discordAuthManager;

        private readonly IMediator _mediator;

        public Handler(ClemBotContext context,
            ILogger<Handler> logger,
            IHttpContextAccessor httpContextAccessor,
            IDiscordAuthManager discordAuthManager,
            IMediator mediator)
        {
            _context = context;
            _logger = logger;
            _httpContextAccessor = httpContextAccessor;
            _discordAuthManager = discordAuthManager;
            _mediator = mediator;
        }

        public async Task<IAuthorizeResult<Model>> Handle(Query request, CancellationToken cancellationTokeln)
        {
            _httpContextAccessor.HttpContext!.Request.Headers.TryGetValue("Origin", out var origin);
            _logger.LogInformation("Site User Request Initialized from Url: {Origin}", origin);

            var token = _httpContextAccessor.HttpContext.User.FindFirst(Claims.DiscordBearer)?.Value;

            if (token is null)
            {
                _logger.LogWarning("Api User Request Denied: No Bearer Token Found");
                return AuthorizeResult<Model>.Forbidden();
            }

            var discordUser = await _discordAuthManager.GetDiscordUserAsync(token);
            if (discordUser is null)
            {
                _logger.LogWarning("Api User Request Denied: Invalid Discord Token");
                return AuthorizeResult<Model>.Forbidden();
            }

            var userGuilds = await _discordAuthManager.GetDiscordUserGuildsAsync(token);
            if (userGuilds is null)
            {
                _logger.LogWarning("Api User Guilds Request Denied: Invalid Discord Token");
                return AuthorizeResult<Model>.Forbidden();
            }

            var addedGuilds = await _context.GuildUser
                .Where(x => x.UserId == ulong.Parse(discordUser.User.Id))
                .Select(y => y.GuildId.ToString())
                .ToListAsync();

            var userClaims = await _context.Users.GetUserClaimsAsync(ulong.Parse(discordUser.User.Id));
            foreach (var guild in userGuilds)
            {
                guild.IsAdded = addedGuilds.Contains(guild.Id);

               if (userClaims.TryGetValue(ulong.Parse(guild.Id), out var claims))
               {
                   guild.Claims = claims.Select(x => x.ToString()).ToList();
               }
            }

            var siteUser = new SiteUser {User = discordUser, Guilds = userGuilds};

            _logger.LogInformation("Site Login Request Accepted");
            return AuthorizeResult<Model>.Success(new Model {User = siteUser});
        }
    }
}
