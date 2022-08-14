using ClemBot.Api.Data.Contexts;
using ClemBot.Api.Data.Extensions;
using Microsoft.EntityFrameworkCore;

namespace ClemBot.Api.Core.Features.Users.Bot;

public class GetGuildClaims
{
    public class Query : IRequest<QueryResult<IEnumerable<BotAuthClaims>>>
    {
        public ulong GuildId { get; init; }

        public ulong UserId { get; init; }
    }

    public record QueryHandler(ClemBotContext _context) : IRequestHandler<Query, QueryResult<IEnumerable<BotAuthClaims>>>
    {
        public async Task<QueryResult<IEnumerable<BotAuthClaims>>> Handle(Query request, CancellationToken cancellationToken)
        {
           var claims = await _context.Users.GetUserGuildClaimsAsync(request.GuildId, request.UserId);
           return QueryResult<IEnumerable<BotAuthClaims>>.Success(claims);
        }
    }
}
