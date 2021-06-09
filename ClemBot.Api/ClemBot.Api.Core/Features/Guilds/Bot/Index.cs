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
    public class Index
    {
        public class Query : IRequest<Result<IEnumerable<Model>, QueryStatus>>
        {
        }

        public class Model
        {
            public ulong Id { get; set; }

            public string Name { get; set; } = null!;

            public string? WelcomeMessage { get; set; }
        }

        public record Handler(ClemBotContext _context) : IRequestHandler<Query, Result<IEnumerable<Model>, QueryStatus>>
        {
            public async Task<Result<IEnumerable<Model>, QueryStatus>> Handle(Query request,
                CancellationToken cancellationToken)
            {
                var guilds = await _context.Guilds.ToListAsync();

                if (!guilds.Any())
                {
                    return QueryResult<IEnumerable<Model>>.NotFound();
                }

                return QueryResult<IEnumerable<Model>>.Success(
                    guilds.Select(x => new Model { Id = x.Id, Name = x.Name, WelcomeMessage = x.WelcomeMessage }));
            }
        }
    }
}
