using System.Collections.Generic;
using System.Linq;
using System.Threading;
using System.Threading.Tasks;
using ClemBot.Api.Common.Utilities;
using ClemBot.Api.Data.Contexts;
using ClemBot.Api.Services.Caching.GlobalStats.Models;
using MediatR;
using Microsoft.EntityFrameworkCore;

namespace ClemBot.Api.Core.Features.Public;

public class GlobalStats
{
    public class Query : IRequest<IQueryResult<Model>>
    {
    }

    public class Model
    {
        public int Guilds { get; set; }

        public int Users { get; set; }

        public int Commands { get; set;  }
    }

    public record Handler(ClemBotContext _context, IMediator _mediator) : IRequestHandler<Query, IQueryResult<Model>>
    {
        public async Task<IQueryResult<Model>> Handle(Query request,
            CancellationToken cancellationToken)
        {
            var guildsCount = await _mediator.Send(new GlobalGuildStatsRequest());

            var usersCount = await _mediator.Send(new GlobalUserStatsRequest());

            var commandsCount = await _mediator.Send(new GlobalCommandStatsRequest());

            return QueryResult<Model>.Success(new Model()
            {
                Guilds = guildsCount,
                Users = usersCount,
                Commands = commandsCount
            });
        }
    }

}
