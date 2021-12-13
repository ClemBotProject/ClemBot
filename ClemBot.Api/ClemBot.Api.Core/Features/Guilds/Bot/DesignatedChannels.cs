using System.Collections.Generic;
using System.Linq;
using System.Threading;
using System.Threading.Tasks;
using ClemBot.Api.Common.Utilities;
using ClemBot.Api.Data.Contexts;
using MediatR;
using Microsoft.EntityFrameworkCore;

namespace ClemBot.Api.Core.Features.Guilds.Bot;

public class DesignatedChannels
{
    public class Query : IRequest<IQueryResult<IEnumerable<Model>>>
    {
        public ulong Id { get; set; }
    }

    public class Model
    {
        public Common.Enums.DesignatedChannels Designation { get; set; }

        public IEnumerable<ulong> ChannelIds { get; set; } = new List<ulong>();
    }

    public record Handler(ClemBotContext _context) :
        IRequestHandler<Query, IQueryResult<IEnumerable<Model>>>
    {
        public async Task<IQueryResult<IEnumerable<Model>>> Handle(Query request, CancellationToken cancellationToken)
        {
            var designatedChannels = await _context.DesignatedChannelMappings
                .Where(x => x.Channel.Guild.Id == request.Id)
                .ToListAsync();

            return QueryResult<IEnumerable<Model>>.Success(designatedChannels
                .GroupBy(y => y.Type)
                .Select(y => new Model()
                {
                    Designation = y.Key,
                    ChannelIds = y.Select(z => z.ChannelId)
                }));
        }
    }
}
