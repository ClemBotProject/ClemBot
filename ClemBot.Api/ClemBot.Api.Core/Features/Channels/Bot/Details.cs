using System.Linq;
using System.Threading;
using System.Threading.Tasks;
using ClemBot.Api.Core.Utilities;
using ClemBot.Api.Data.Contexts;
using MediatR;
using Microsoft.EntityFrameworkCore;

namespace ClemBot.Api.Core.Features.Channels.Bot
{
    public class Details
    {
        public class Query : IRequest<Result<Model, QueryStatus>>
        {
            public ulong Id { get; init; }
        }

        public class Model
        {
            public ulong Id { get; init; }

            public string? Name { get; init; }

            public ulong GuildId { get; init; }

            public bool IsAssignable { get; init; }
        }

        public record QueryHandler(ClemBotContext _context) : IRequestHandler<Query, Result<Model, QueryStatus>>
        {
            public async Task<Result<Model, QueryStatus>> Handle(Query request, CancellationToken cancellationToken)
            {
                var channel = await _context.Channels
                    .Where(x => x.Id == request.Id)
                    .FirstAsync();

                if (channel is null)
                {
                    return QueryResult<Model>.NotFound();
                }

                return QueryResult<Model>.Success(new Model()
                {
                    Id = channel.Id,
                    Name = channel.Name,
                    GuildId = channel.GuildId
                });
            }
        }
    }
}
