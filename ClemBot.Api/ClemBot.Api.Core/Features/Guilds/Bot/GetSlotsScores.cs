using ClemBot.Api.Common;
using ClemBot.Api.Data.Contexts;
using Microsoft.EntityFrameworkCore;

namespace ClemBot.Api.Core.Features.Guilds.Bot;

public class GetSlotsScores
{
    public record Query : IRequest<IQueryResult<Model>>
    {
        public ulong GuildId { get; init; }

        public bool Leader { get; init; }

        public int Limit { get; init; }
    }

    public record Model : IResponseModel
    {
        public IEnumerable<Score> Scores { get; init; } = null!;
    }

    public record Score
    {
        public ulong HighScore { get; init; }

        public ulong UserId { get; init; }
    }

    public class QueryHandler : IRequestHandler<Query, IQueryResult<Model>>
    {
        public ClemBotContext _context { get; init; }

        public QueryHandler(ClemBotContext context)
        {
            _context = context;
        }

        public async Task<IQueryResult<Model>> Handle(Query request, CancellationToken cancellationToken)
        {
            var scores = await _context.SlotScores
                .Where(x => x.GuildId == request.GuildId)
                .QueryIfElse(() => request.Leader,
                    q => q.OrderByDescending(y => y.Score),
                    q => q.OrderBy(y => y.Score))
                .Select(z => new { z.Score, z.UserId })
                .Take(request.Limit)
                .ToListAsync();

            return QueryResult<Model>.Success(new Model
            {
                Scores = scores.Select(x => new Score
                {
                    HighScore = x.Score,
                    UserId = x.UserId
                })
            });
        }
    }
}
