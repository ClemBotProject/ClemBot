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

namespace ClemBot.Api.Core.Features.Guilds.Bot;

public class Threads
{
    public class Query : IRequest<IQueryResult<IEnumerable<Model>>>
    {
        public ulong Id { get; init; }
    }

    public class Model
    {
        public ulong Id { get; init; }

        public string? Name { get; init; }

        public ulong ParentId { get; set; }
    }

    public record QueryHandler(ClemBotContext _context)
        : IRequestHandler<Query, IQueryResult<IEnumerable<Model>>>
    {
        public async Task<IQueryResult<IEnumerable<Model>>> Handle(Query request,
            CancellationToken cancellationToken)
        {
            var threads = await _context.Channels
                .Where(x => x.GuildId == request.Id && x.IsThread)
                .ToListAsync();

            if (threads is null)
            {
                return QueryResult<IEnumerable<Model>>.NotFound();
            }

            return QueryResult<IEnumerable<Model>>.Success(threads
                .Select(t => new Model
                {
                    Id = t.Id,
                    Name = t.Name,
                    ParentId = t.ParentId ??
                               throw new EntityStateException<Channel>("Channel object ParentId is null while IsThread is true", t)
                }));
        }
    }
}
