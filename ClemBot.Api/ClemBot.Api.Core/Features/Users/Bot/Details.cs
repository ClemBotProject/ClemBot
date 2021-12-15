using ClemBot.Api.Common.Utilities;
using ClemBot.Api.Data.Contexts;
using MediatR;
using Microsoft.EntityFrameworkCore;

namespace ClemBot.Api.Core.Features.Users.Bot;

public class Details
{
    public class Query : IRequest<IQueryResult<Model>>
    {
        public ulong Id { get; set; }
    }

    public class Model
    {
        public ulong Id { get; set; }

        public string? Name { get; set; }

        public List<ulong> Guilds { get; set; } = new();
    }

    public record QueryHandler(ClemBotContext _context) : IRequestHandler<Query, IQueryResult<Model>>
    {
        public async Task<IQueryResult<Model>> Handle(Query request, CancellationToken cancellationToken)
        {
            var user = await _context.Users
                .Where(x => x.Id == request.Id)
                .Include(y => y.Guilds)
                .FirstOrDefaultAsync();

            if (user is null)
            {
                return QueryResult<Model>.NotFound();
            }

            return QueryResult<Model>.Success(new Model()
            {
                Id = user.Id,
                Name = user.Name,
                Guilds = user.Guilds.Select(x => x.Id).ToList()
            });
        }
    }
}
