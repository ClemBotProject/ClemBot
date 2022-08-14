using System.Collections.Generic;
using System.Linq;
using System.Threading;
using System.Threading.Tasks;
using ClemBot.Api.Common.Utilities;
using ClemBot.Api.Data.Contexts;
using MediatR;
using Microsoft.EntityFrameworkCore;

namespace ClemBot.Api.Core.Features.Channels.Bot;

public class Index
{
    public class Query : IRequest<QueryResult<IEnumerable<Model>>>
    {
    }

    public class Model
    {
        public ulong Id { get; set; }

        public string Name { get; set; } = null!;

        public ulong GuildId { get; set; }
    }

    public record Handler(ClemBotContext _context) : IRequestHandler<Query, QueryResult<IEnumerable<Model>>>
    {
        public async Task<QueryResult<IEnumerable<Model>>> Handle(Query request, CancellationToken cancellationToken)
        {
            var channels = await _context.Channels
                .Where(x => !x.IsThread)
                .ToListAsync();

            if (!channels.Any())
            {
                return QueryResult<IEnumerable<Model>>.NotFound();
            }

            return QueryResult<IEnumerable<Model>>.Success(
                channels.Select(x => new Model()
                {
                    Id = x.Id,
                    Name = x.Name,
                    GuildId = x.GuildId
                }));
        }
    }
}
