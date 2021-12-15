using System.Collections.Generic;
using System.Linq;
using System.Threading;
using System.Threading.Tasks;
using ClemBot.Api.Common.Utilities;
using ClemBot.Api.Data.Contexts;
using MediatR;
using Microsoft.EntityFrameworkCore;

namespace ClemBot.Api.Core.Features.DesignatedChannels.Bot;

public class Details
{
    public class Command : IRequest<IQueryResult<Model>>
    {
        public ulong GuildId { get; init; }

        public Common.Enums.DesignatedChannels Designation { get; set; }
    }

    public class Model
    {
        public IEnumerable<ulong> Mappings { get; set; } = null!;
    }

    public record QueryHandler(ClemBotContext _context) : IRequestHandler<Command, IQueryResult<Model>>
    {
        public async Task<IQueryResult<Model>> Handle(Command request, CancellationToken cancellationToken)
        {
            var channels = await _context.DesignatedChannelMappings
                .Where(x => x.Channel.Guild.Id == request.GuildId && x.Type == request.Designation)
                .ToListAsync();

            return QueryResult<Model>.Success(new Model()
            {
                Mappings = channels.Select(x => x.ChannelId)
            });
        }
    }
}
