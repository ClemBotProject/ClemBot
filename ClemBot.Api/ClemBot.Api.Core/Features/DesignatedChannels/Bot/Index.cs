using System.Collections.Generic;
using System.Linq;
using System.Threading;
using System.Threading.Tasks;
using ClemBot.Api.Core.Utilities;
using ClemBot.Api.Data.Contexts;
using MediatR;
using Microsoft.EntityFrameworkCore;

namespace ClemBot.Api.Core.Features.DesignatedChannels.Bot
{
    public class Index
    {
        public class Query : IRequest<Result<IEnumerable<ulong>, QueryStatus>>
        {
            public Data.Enums.DesignatedChannels Designation { get; set; }
        }

        public record Handler(ClemBotContext _context) :
            IRequestHandler<Query, Result<IEnumerable<ulong>, QueryStatus>>
        {
            public async Task<Result<IEnumerable<ulong>, QueryStatus>> Handle(Query request, CancellationToken cancellationToken)
            {
                var designatedChannels = await _context.DesignatedChannelMappings
                    .Where(x => x.Type == request.Designation)
                    .Select(y => y.ChannelId)
                    .ToListAsync();

                return QueryResult<IEnumerable<ulong>>.Success(designatedChannels);
            }
        }
    }
}
