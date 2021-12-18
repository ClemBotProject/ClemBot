using ClemBot.Api.Data.Contexts;
using ClemBot.Api.Data.Extensions;
using Microsoft.EntityFrameworkCore;

namespace ClemBot.Api.Core.Features.Users.Bot;

public class GetGuildClaims
{
    public class Query : IRequest<IQueryResult<IEnumerable<BotAuthClaims>>>
    {
        public ulong GuildId { get; init; }

        public ulong UserId { get; init; }
    }

    public record QueryHandler(ClemBotContext _context) : IRequestHandler<Query, IQueryResult<IEnumerable<BotAuthClaims>>>
    {
        public async Task<IQueryResult<IEnumerable<BotAuthClaims>>> Handle(Query request, CancellationToken cancellationToken)
        {
           var claims = await _context.Users.GetUserGuildClaimsAsync(request.GuildId, request.UserId);
           return QueryResult<IEnumerable<BotAuthClaims>>.Success(claims);
        }
    }
}
