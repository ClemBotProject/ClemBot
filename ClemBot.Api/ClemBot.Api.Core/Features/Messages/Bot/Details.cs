using System;
using System.Linq;
using System.Threading;
using System.Threading.Tasks;
using ClemBot.Api.Common.Utilities;
using ClemBot.Api.Data.Contexts;
using MediatR;
using Microsoft.EntityFrameworkCore;

namespace ClemBot.Api.Core.Features.Messages.Bot;

public class Details
{
    public class Query : IRequest<IQueryResult<Model>>
    {
        public ulong Id { get; set; }
    }

    public class Model
    {
        public ulong Id { get; set; }

        public string Content { get; set; } = null!;

        public ulong GuildId { get; set; }

        public ulong ChannelId { get; set; }

        public ulong UserId { get; set; }
    }

    public record QueryHandler(ClemBotContext _context) : IRequestHandler<Query, IQueryResult<Model>>
    {
        public async Task<IQueryResult<Model>> Handle(Query request, CancellationToken cancellationToken)
        {
            var message = await _context.Messages
                .Where(x => x.Id == request.Id)
                .Include(y => y.Contents)
                .FirstOrDefaultAsync();

            if (message is null)
            {
                return QueryResult<Model>.NotFound();
            }

            return QueryResult<Model>.Success(new Model()
            {
                Id = message.Id,
                Content = message.Contents.Last().Content,
                ChannelId = message.ChannelId,
                GuildId = message.GuildId,
                UserId = message.UserId
            });
        }
    }
}
