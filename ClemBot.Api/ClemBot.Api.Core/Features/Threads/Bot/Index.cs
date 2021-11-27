using System.Collections.Generic;
using System.Linq;
using System.Threading;
using System.Threading.Tasks;
using ClemBot.Api.Common.Utilities;
using ClemBot.Api.Data.Contexts;
using ClemBot.Api.Data.Exceptions;
using ClemBot.Api.Data.Models;
using MediatR;
using Microsoft.EntityFrameworkCore;

namespace ClemBot.Api.Core.Features.Threads.Bot;

public class Index
{
    public class Query : IRequest<IQueryResult<IEnumerable<Model>>>
    {
    }

    public class Model
    {
        public ulong Id { get; set; }

        public string Name { get; set; } = null!;

        public ulong GuildId { get; set; }

        public ulong ParentId { get; set; }
    }

    public record Handler(ClemBotContext _context) : IRequestHandler<Query, IQueryResult<IEnumerable<Model>>>
    {
        public async Task<IQueryResult<IEnumerable<Model>>> Handle(Query request, CancellationToken cancellationToken)
        {
            var threads = await _context.Channels
                .Where(x => x.IsThread)
                .ToListAsync();

            if (!threads.Any())
            {
                return QueryResult<IEnumerable<Model>>.NotFound();
            }

            return QueryResult<IEnumerable<Model>>.Success(
                threads.Select(x => new Model()
                {
                    Id = x.Id,
                    Name = x.Name,
                    GuildId = x.GuildId,
                    ParentId = x.ParentId ??
                               throw new EntityStateException<Channel>("Channel object ParentId is null while IsThread is true", x)
                }));
        }
    }
}
