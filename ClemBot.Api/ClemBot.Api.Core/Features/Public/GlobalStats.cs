using System.Collections.Generic;
using System.Linq;
using System.Threading;
using System.Threading.Tasks;
using ClemBot.Api.Core.Utilities;
using ClemBot.Api.Data.Contexts;
using ClemBot.Api.Services.GlobalStats;
using ClemBot.Api.Services.GlobalStats.Models;
using MediatR;
using Microsoft.EntityFrameworkCore;

namespace ClemBot.Api.Core.Features.Public
{
    public class GlobalStats
    {
        public class Query : IRequest<Result<Model, QueryStatus>>
        {
        }

        public class Model
        {
            public int Guilds { get; set; }

            public int Users { get; set; }

            public int Commands { get; set;  }
        }

        public record Handler(ClemBotContext _context, IMediator _mediator) : IRequestHandler<Query, Result<Model, QueryStatus>>
        {
            public async Task<Result<Model, QueryStatus>> Handle(Query request,
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
}
