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
    public class Details
    {
        public class Query : IRequest<Result<Model, QueryStatus>>
        {
            public ulong Id { get; set; }
        }

        public class Model
        {
            public ulong Id { get; set; }

            public string? Name { get; set; }

            public string? WelcomeMessage { get; set; }

            public List<ulong> Users { get; set; } = new();
        }

        public record QueryHandler(ClemBotContext _context) : IRequestHandler<Query, Result<Model, QueryStatus>>
        {
            public async Task<Result<Model, QueryStatus>> Handle(Query request, CancellationToken cancellationToken)
            {
                var guild = await _context.Guilds
                    .Where(x => x.Id == request.Id)
                    .Include(y => y.Users)
                    .FirstOrDefaultAsync();

                if (guild is null)
                {
                    return QueryResult<Model>.NotFound();
                }

                return QueryResult<Model>.Success(new Model
                {
                    Id = guild.Id,
                    Name = guild.Name,
                    WelcomeMessage = guild.WelcomeMessage,
                    Users = guild.Users.Select(x => x.Id).ToList()
                });
            }
        }
    }
}
