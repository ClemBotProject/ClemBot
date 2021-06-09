using System.Collections.Generic;
using System.Linq;
using System.Threading;
using System.Threading.Tasks;
using ClemBot.Api.Core.Utilities;
using ClemBot.Api.Data.Contexts;
using MediatR;
using Microsoft.EntityFrameworkCore;

namespace ClemBot.Api.Core.Features.Guilds.Bot
{
    public class DesignatedChannels
    {
        public class Query : IRequest<Result<IEnumerable<Model>, QueryStatus>>
        {
            public ulong Id { get; set; }
        }

        public class Model
        {
            public Data.Enums.DesignatedChannels Designation { get; set; }

            public IEnumerable<ulong> ChannelIds { get; set; } = new List<ulong>();
        }

        public record Handler(ClemBotContext _context) :
            IRequestHandler<Query, Result<IEnumerable<Model>, QueryStatus>>
        {
            public async Task<Result<IEnumerable<Model>, QueryStatus>> Handle(Query request, CancellationToken cancellationToken)
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
}
