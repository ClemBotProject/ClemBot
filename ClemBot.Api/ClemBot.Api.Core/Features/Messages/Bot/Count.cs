using System;
using System.Linq;
using System.Threading;
using System.Threading.Tasks;
using ClemBot.Api.Core.Features.Tags;
using ClemBot.Api.Core.Utilities;
using ClemBot.Api.Data.Contexts;
using MediatR;
using Microsoft.EntityFrameworkCore;
using System.Collections.Generic;
using System.Diagnostics.CodeAnalysis;

namespace ClemBot.Api.Core.Features.Messages.Bot
{
    public class Count
    {
        public class Query : IRequest<Result<Model, QueryStatus>>
        {
            public ulong UserId { get; set;  }
            public ulong GuildId { get; set; }
            public int Days { get; set; }
        }

        public class Model
        {
            public int MessageCount { get; set; }
        }

        public record QueryHandler(ClemBotContext _context) : IRequestHandler<Query, Result<Model, QueryStatus>>
        {
            public async Task<Result<Model, QueryStatus>> Handle(Query request,
                CancellationToken cancellationToken)
            {
                var dayOffset = DateTime.Now.Subtract(new TimeSpan(days: request.Days, hours: 0, minutes: 0, seconds: 0));
                var messages = await _context.MessageContents
                    .Include(z => z.Message)
                    .Where(y => y.Time > dayOffset && y.Message.UserId == request.UserId && y.Message.GuildId == request.GuildId)
                    .GroupBy(x => x.MessageId)
                    .CountAsync();

                return QueryResult<Model>.Success(new Model()
                {
                    MessageCount = messages
                });
            }
        }
    }
}
