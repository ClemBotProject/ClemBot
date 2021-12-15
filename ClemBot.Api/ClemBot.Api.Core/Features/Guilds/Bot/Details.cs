using System.Collections.Generic;
using System.Linq;
using System.Threading;
using System.Threading.Tasks;
using ClemBot.Api.Common.Utilities;
using ClemBot.Api.Data.Contexts;
using MediatR;
using Microsoft.EntityFrameworkCore;

namespace ClemBot.Api.Core.Features.Guilds.Bot;

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

        public string? WelcomeMessage { get; set; }
    }

    public record QueryHandler(ClemBotContext _context) : IRequestHandler<Query, IQueryResult<Model>>
    {
        public async Task<IQueryResult<Model>> Handle(Query request, CancellationToken cancellationToken)
        {
            var guild = await _context.Guilds
                .FirstOrDefaultAsync(x => x.Id == request.Id);

            if (guild is null)
            {
                return QueryResult<Model>.NotFound();
            }

            return QueryResult<Model>.Success(new Model
            {
                Id = guild.Id,
                Name = guild.Name,
                WelcomeMessage = guild.WelcomeMessage,
            });
        }
    }
}
