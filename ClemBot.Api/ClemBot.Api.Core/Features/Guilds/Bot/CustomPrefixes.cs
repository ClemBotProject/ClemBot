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
    public class CustomPrefixes
    {
        public class Query : IRequest<Result<IEnumerable<string>, QueryStatus>>
        {
            public ulong Id { get; init; }
        }

        public record QueryHandler(ClemBotContext _context)
            : IRequestHandler<Query, Result<IEnumerable<string>, QueryStatus>>
        {
            public async Task<Result<IEnumerable<string>, QueryStatus>> Handle(Query request,
                CancellationToken cancellationToken)
            {
                var prefixes = await _context.CustomPrefixs
                    .Where(x => x.Guild.Id == request.Id)
                    .Select(y => y.Prefix)
                    .ToListAsync();

                return QueryResult<IEnumerable<string>>.Success(prefixes);
            }
        }
    }
}
