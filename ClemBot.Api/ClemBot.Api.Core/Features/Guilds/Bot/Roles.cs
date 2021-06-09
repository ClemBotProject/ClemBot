using System.Collections.Generic;
using System.Linq;
using System.Threading;
using System.Threading.Tasks;
using ClemBot.Api.Core.Utilities;
using ClemBot.Api.Data.Contexts;
using MediatR;
using Microsoft.EntityFrameworkCore;

namespace ClemBot.Api.Core.Features.Guilds.Bot
{
    public class Roles
    {
        public class Query : IRequest<Result<IEnumerable<Model>, QueryStatus>>
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
            : IRequestHandler<Query, Result<IEnumerable<Model>, QueryStatus>>
        {
            public async Task<Result<IEnumerable<Model>, QueryStatus>> Handle(Query request,
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
}
