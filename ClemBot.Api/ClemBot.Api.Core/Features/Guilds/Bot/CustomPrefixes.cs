using System.Collections.Generic;
using System.Linq;
using System.Threading;
using System.Threading.Tasks;
using ClemBot.Api.Core.Utilities;
using ClemBot.Api.Data.Contexts;
using ClemBot.Api.Services.CustomPrefix.Models;
using MediatR;
using Microsoft.EntityFrameworkCore;

namespace ClemBot.Api.Core.Features.Guilds.Bot;

public class CustomPrefixes
{
    public class Query : IRequest<Result<IEnumerable<string>, QueryStatus>>
    {
        public ulong Id { get; init; }
    }

    public record QueryHandler(ClemBotContext _context, IMediator _mediator)
        : IRequestHandler<Query, Result<IEnumerable<string>, QueryStatus>>
    {
        public async Task<Result<IEnumerable<string>, QueryStatus>> Handle(Query request,
            CancellationToken cancellationToken)
        {
            var prefixes = await _mediator.Send(new GetCustomPrefixRequest { Id = request.Id });

            return QueryResult<IEnumerable<string>>.Success(prefixes);
        }
    }
}