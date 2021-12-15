using System.Collections.Generic;
using System.Linq;
using System.Threading;
using System.Threading.Tasks;
using ClemBot.Api.Common.Utilities;
using ClemBot.Api.Data.Contexts;
using MediatR;
using Microsoft.EntityFrameworkCore;

namespace ClemBot.Api.Core.Features.Guilds.Bot;

public class Roles
{
    public class Query : IRequest<IQueryResult<IEnumerable<Model>>>
    {
        public ulong Id { get; init; }
    }

    public class Model
    {
        public ulong Id { get; init; }

        public string? Name { get; init; }

        public bool IsAssignable { get; init; }
    }

    public record QueryHandler(ClemBotContext _context)
        : IRequestHandler<Query, IQueryResult<IEnumerable<Model>>>
    {
        public async Task<IQueryResult<IEnumerable<Model>>> Handle(Query request,
            CancellationToken cancellationToken)
        {
            var roles = await _context.Roles
                .Where(x => x.GuildId == request.Id)
                .ToListAsync();

            if (roles is null)
            {
                return QueryResult<IEnumerable<Model>>.NotFound();
            }

            return QueryResult<IEnumerable<Model>>.Success(roles
                .Select(role => new Model
                {
                    Id = role.Id,
                    Name = role.Name,
                    IsAssignable = role.IsAssignable ?? false
                }));
        }
    }
}
