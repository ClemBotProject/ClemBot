using System.Threading;
using System.Threading.Tasks;
using ClemBot.Api.Common.Utilities;
using ClemBot.Api.Data.Contexts;
using MediatR;
using Microsoft.EntityFrameworkCore;

namespace ClemBot.Api.Core.Features.Infractions.Bot;

public class Delete
{
    public class Command : IRequest<IQueryResult<int>>
    {
        public int Id { get; init; }
    }

    public record QueryHandler(ClemBotContext _context) : IRequestHandler<Command, IQueryResult<int>>
    {
        public async Task<IQueryResult<int>> Handle(Command request, CancellationToken cancellationToken)
        {
            var infraction = await _context.Infractions
                .FirstOrDefaultAsync(x => x.Id == request.Id);

            if (infraction is null)
            {
                return QueryResult<int>.NotFound();
            }

            _context.Infractions.Remove(infraction);

            await _context.SaveChangesAsync();

            return QueryResult<int>.Success(infraction.Id);
        }
    }
}
