using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading;
using System.Threading.Tasks;
using ClemBot.Api.Common.Enums;
using ClemBot.Api.Common.Utilities;
using ClemBot.Api.Data.Contexts;
using ClemBot.Api.Data.Models;
using MediatR;
using Microsoft.EntityFrameworkCore;

namespace ClemBot.Api.Core.Features.Roles.Bot;

public class Claims
{
    public class Query : IRequest<IQueryResult<IEnumerable<BotAuthClaims>>>
    {
        public ulong Id { get; init; }
    }

    public record QueryHandler(ClemBotContext _context) : IRequestHandler<Query, IQueryResult<IEnumerable<BotAuthClaims>>>
    {
        public async Task<IQueryResult<IEnumerable<BotAuthClaims>>> Handle(Query request, CancellationToken cancellationToken)
        {
            var role = await _context.Roles
                .Where(x => x.Id == request.Id)
                .Include(y => y.Claims)
                .FirstOrDefaultAsync();

            if (role is null)
            {
                return QueryResult<IEnumerable<BotAuthClaims>>.NotFound();
            }

            // Role is admin and has full claim permissions no matter what
            if (role.Admin)
            {
                return QueryResult<IEnumerable<BotAuthClaims>>.Success(Enum.GetValues<BotAuthClaims>());
            }

            return QueryResult<IEnumerable<BotAuthClaims>>.Success(role.Claims.Select(x => x.Claim));
        }
    }
}
