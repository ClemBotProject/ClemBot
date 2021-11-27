using System.Threading;
using System.Threading.Tasks;
using ClemBot.Api.Common.Utilities;
using ClemBot.Api.Data.Contexts;
using MediatR;
using Microsoft.EntityFrameworkCore;

namespace ClemBot.Api.Core.Features.Infractions.Bot;

public class Deactivate
{
    public class Query : IRequest<IQueryResult<int>>
    {
        public int Id { get; set; }
    }

    public record QueryHandler(ClemBotContext _context) : IRequestHandler<Query, IQueryResult<int>>
    {
        public async Task<IQueryResult<int>> Handle(Query request, CancellationToken cancellationToken)
        {
            var infraction = await _context.Infractions
                .FirstOrDefaultAsync(x => x.Id == request.Id);

            if (infraction is null)
            {
                return QueryResult<int>.NotFound();
            }

            infraction.IsActive = false;
            await _context.SaveChangesAsync();

            return QueryResult<int>.Success(infraction.Id);
        }
    }
}
