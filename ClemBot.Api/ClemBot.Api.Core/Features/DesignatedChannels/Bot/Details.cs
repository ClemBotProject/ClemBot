using System.Collections.Generic;
using System.Linq;
using System.Threading;
using System.Threading.Tasks;
using ClemBot.Api.Common.Utilities;
using ClemBot.Api.Data.Contexts;
using ClemBot.Api.Services.Caching.DesignatedChannels.Models;
using MediatR;
using Microsoft.EntityFrameworkCore;

namespace ClemBot.Api.Core.Features.DesignatedChannels.Bot;

public class Details
{
    public class Command : IRequest<QueryResult<Model>>
    {
        public ulong GuildId { get; init; }

        public Common.Enums.DesignatedChannels Designation { get; set; }
    }

    public class Model
    {
        public IEnumerable<ulong> Mappings { get; set; } = null!;
    }

    public class QueryHandler : IRequestHandler<Command, QueryResult<Model>>
    {
        private readonly IMediator _mediator;

        public QueryHandler(IMediator mediator)
        {
            _mediator = mediator;
        }

        public async Task<QueryResult<Model>> Handle(Command request, CancellationToken cancellationToken)
        {
            var channels = await _mediator.Send(new GetDesignatedChannelDetailRequest { Id = request.GuildId, Designation = request.Designation });

            return QueryResult<Model>.Success(new Model
            {
                Mappings = channels.Select(x => x.ChannelId)
            });
        }
    }
}
