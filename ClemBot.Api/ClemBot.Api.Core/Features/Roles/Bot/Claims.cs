using System.Collections.Generic;
using System.Linq;
using System.Threading;
using System.Threading.Tasks;
using ClemBot.Api.Core.Utilities;
using ClemBot.Api.Data.Contexts;
using ClemBot.Api.Data.Enums;
using ClemBot.Api.Data.Models;
using MediatR;
using Microsoft.EntityFrameworkCore;

namespace ClemBot.Api.Core.Features.Roles.Bot
{
    public class Claims
    {
        public class Query : IRequest<Result<IEnumerable<BotAuthClaims>, QueryStatus>>
        {
            public ulong Id { get; init; }
        }

        public record QueryHandler(ClemBotContext _context) : IRequestHandler<Query, Result<IEnumerable<BotAuthClaims>, QueryStatus>>
        {
            public async Task<Result<IEnumerable<BotAuthClaims>, QueryStatus>> Handle(Query request, CancellationToken cancellationToken)
            {
                var role = await _context.Roles
                    .Where(x => x.Id == request.Id)
                    .Include(y => y.Claims)
                    .FirstOrDefaultAsync();

                if (role is null)
                {
                    return QueryResult<IEnumerable<BotAuthClaims>>.NotFound();
                }

                return QueryResult<IEnumerable<BotAuthClaims>>.Success(role.Claims.Select(x => x.Claim));
            }
        }
    }
}
