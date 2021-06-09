using System;
using System.Linq;
using System.Threading;
using System.Threading.Tasks;
using ClemBot.Api.Core.Utilities;
using ClemBot.Api.Data.Contexts;
using MediatR;
using Microsoft.EntityFrameworkCore;

namespace ClemBot.Api.Core.Features.Tags
{
    public class Details
    {
        public class Query : IRequest<Result<Model, QueryStatus>>
        {
            public ulong GuildId { get; set; }

            public string Name { get; set; } = null!;
        }

        public class Model
        {
            public string Name { get; set; } = null!;

            public string Content { get; set; } = null!;

            public DateTime Time { get; set; }

            public ulong GuildId { get; set; }

            public ulong UserId { get; set; }

            public int UseCount { get; set; }
        }

        public record QueryHandler(ClemBotContext _context) : IRequestHandler<Query, Result<Model, QueryStatus>>
        {
            public async Task<Result<Model, QueryStatus>> Handle(Query request, CancellationToken cancellationToken)
            {
                var tag = await _context.Tags
                    .Where(g => g.GuildId == request.GuildId && g.Name == request.Name)
                    .Include(y => y.TagUses)
                    .FirstOrDefaultAsync();

                if (tag is null)
                {
                    return QueryResult<Model>.NotFound();
                }

                return QueryResult<Model>.Success(new Model()
                {
                    Name = tag.Name,
                    Content = tag.Content,
                    Time = tag.Time,
                    GuildId = tag.GuildId,
                    UserId = tag.UserId,
                    UseCount = tag.TagUses.Count
                });
            }
        }
    }
}
