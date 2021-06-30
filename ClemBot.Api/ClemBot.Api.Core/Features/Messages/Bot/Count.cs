using System.Linq;
using System.Threading;
using System.Threading.Tasks;
using ClemBot.Api.Core.Features.Tags;
using ClemBot.Api.Core.Utilities;
using ClemBot.Api.Data.Contexts;
using MediatR;
using Microsoft.EntityFrameworkCore;
using System.Collections.Generic;
namespace ClemBot.Api.Core.Features.Messages.Bot
{
    public class Count
    {
        public class Query : IRequest<Result<Model, QueryStatus>>
        {
            public ulong UserId { get; set;  }
        }

        public class Model
        {
            public List<ulong> Messages { get; set; } = new();

            public ulong UserId { get; set; }
            public List<ulong> Guilds { get; set; } = new();
        }

        public record QueryHandler(ClemBotContext _context) : IRequestHandler<Query, Result<Model, QueryStatus>>
        {
            public async Task<Result<Model, QueryStatus>> Handle(Query request,
                CancellationToken cancellationToken)
            {
                var messages = await _context.Messages.
                    .Where(x => x.UserId == request.UserId)
                    .Include(y => y.Guild)
                    .FirstOrDefaultAsync();

                if (messages is null)
                {
                    return QueryResult<Model>.NotFound();
                }

                return QueryResult<Model>.Success(messages.);
            }
        }
    }
}
