using ClemBot.Api.Common;
using ClemBot.Api.Data.Contexts;
using Microsoft.EntityFrameworkCore;

namespace ClemBot.Api.Core.Features.Users.Bot;

public class GetSlotsScores
{
    public record Query : IRequest<IQueryResult<Model>>
    {
        public ulong UserId { get; init; }

        public ulong GuildId { get; init; }

        public int Limit { get; init; }
    }

    public record Model : IResponseModel
    {
        public IEnumerable<ulong> Scores { get; init; } = null!;
    }

    public class QueryHandler : IRequestHandler<Query, IQueryResult<Model>>
    {
        private readonly ClemBotContext _context;

        public QueryHandler(ClemBotContext context)
        {
            _context = context;
        }

        public async Task<IQueryResult<Model>> Handle(Query request, CancellationToken cancellationToken)
        {
            var scores = await _context.SlotScores
                .Where(x => x.UserId == request.UserId && x.GuildId == request.GuildId)
                .OrderByDescending(y => y.Score)
                .Take(request.Limit)
                .ToListAsync();

            return QueryResult<Model>.Success(new Model
            {
                Scores = scores.Select(x => x.Score)
            });
        }
    }
}
