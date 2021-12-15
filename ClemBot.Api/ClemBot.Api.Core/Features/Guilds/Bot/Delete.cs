using System.Threading;
using System.Threading.Tasks;
using ClemBot.Api.Common.Utilities;
using ClemBot.Api.Data.Contexts;
using MediatR;
using Microsoft.EntityFrameworkCore;

namespace ClemBot.Api.Core.Features.Guilds.Bot;

public class Delete
{
    public class Query : IRequest<IQueryResult<Model>>
    {
        public ulong Id { get; set; }
    }

    public class Model
    {
        public ulong Id { get; init; }

        public string? Name { get; init; }
    }

    public record QueryHandler(ClemBotContext _context) : IRequestHandler<Query, IQueryResult<Model>>
    {
        public async Task<IQueryResult<Model>> Handle(Query request, CancellationToken cancellationToken)
        {
            var guild = await _context.Guilds
                .FirstOrDefaultAsync(g => g.Id == request.Id);

            if (guild is null)
            {
                return QueryResult<Model>.NotFound();
            }

            _context.Guilds.Remove(guild);
            await _context.SaveChangesAsync();

            return QueryResult<Model>.Success(new Model { Id = guild.Id, Name = guild.Name });
        }
    }
}
