using System.Collections.Generic;
using System.Security.Claims;
using System.Threading;
using System.Threading.Tasks;
using ClemBot.Api.Core.Security;
using ClemBot.Api.Core.Security.JwtToken;
using ClemBot.Api.Core.Security.OAuth;
using ClemBot.Api.Core.Security.OAuth.OAuthUser;
using ClemBot.Api.Core.Utilities;
using ClemBot.Api.Data.Contexts;
using ClemBot.Api.Data.Enums;
using ClemBot.Api.Data.Extensions;
using ClemBot.Api.Services.Guilds.Models;
using LinqToDB;
using LinqToDB.Mapping;
using MediatR;
using Microsoft.AspNetCore.Http;

namespace ClemBot.Api.Core.Features.Authorization;

public class GetSiteUser
{
    public class Query : IRequest<Result<Model, AuthorizeStatus>>
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

    public class Handler : IRequestHandler<Query, Result<Model, AuthorizeStatus>>
    {
        private readonly ClemBotContext _context;

        private readonly ILogger _logger;

        private readonly IHttpContextAccessor _httpContextAccessor;

        private readonly IDiscordAuthManager _discordAuthManager;

        private readonly IMediator _mediator;

        public Handler(ClemBotContext context,
            ILogger logger,
            IHttpContextAccessor httpContextAccessor,
            IDiscordAuthManager discordAuthManager,
            IMediator _mediator)
        {
            _context = context;
            _logger = logger;
            _httpContextAccessor = httpContextAccessor;
            _discordAuthManager = discordAuthManager;
            this._mediator = _mediator;
        }

        public async Task<Result<Model, AuthorizeStatus>> Handle(Query request, CancellationToken cancellationTokeln)
        {
            _httpContextAccessor.HttpContext!.Request.Headers.TryGetValue("Origin", out var origin);
            _logger.Information("Site User Request Initialized from Url: {Origin}", origin);

            var token = _httpContextAccessor.HttpContext.User.FindFirst(Claims.DiscordBearer)?.Value;

            if (token is null)
            {
                _logger.Warning("Api User Request Denied: No Bearer Token Found");
                return AuthorizeResult<Model>.Forbidden();
            }

            var discordUser = await _discordAuthManager.GetDiscordUserAsync(token);
            if (discordUser is null)
            {
                _logger.Warning("Api User Request Denied: Invalid Discord Token");
                return AuthorizeResult<Model>.Forbidden();
            }

            var userGuilds = await _discordAuthManager.GetDiscordUserGuildsAsync(token);
            if (userGuilds is null)
            {
                _logger.Warning("Api User Guilds Request Denied: Invalid Discord Token");
                return AuthorizeResult<Model>.Forbidden();
            }

            var userClaims = await _context.Users.GetUserClaimsAsync(ulong.Parse(discordUser.User.Id));

            foreach (var guild in userGuilds)
            {
                guild.IsAdded = await _mediator.Send(new GuildExistsRequest{Id = ulong.Parse(guild.Id)});

               if (userClaims.TryGetValue(ulong.Parse(guild.Id), out var claims))
               {
                   guild.Claims = claims.Select(x => x.ToString()).ToList();
               }

               // Check if the user has admin in the guild
               // This means they automatically have all the claims
               if ((guild.Permissions & 0x8) == 0x8)
               {
                   guild.Claims = Enum.GetNames(typeof(BotAuthClaims)).ToList();
               }
            }

            var siteUser = new SiteUser {User = discordUser, Guilds = userGuilds};

            _logger.Information("Site Login Request Accepted");
            return AuthorizeResult<Model>.Success(new Model {User = siteUser});
        }
    }
}
