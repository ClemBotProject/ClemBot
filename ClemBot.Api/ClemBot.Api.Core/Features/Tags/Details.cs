using System;
using System.Linq;
using System.Threading;
using System.Threading.Tasks;
using ClemBot.Api.Common.Utilities;
using ClemBot.Api.Data.Contexts;
using MediatR;
using Microsoft.EntityFrameworkCore;

namespace ClemBot.Api.Core.Features.Tags;

public class Details
{
    public class Query : IRequest<IQueryResult<Model>>
    {
        public ulong GuildId { get; set; }

        public string Name { get; set; } = null!;
    }

    public class Model
    {
        public string Name { get; set; } = null!;

        public string Content { get; set; } = null!;

        public string CreationDate { get; set; } = null!;

        public ulong GuildId { get; set; }

        public ulong UserId { get; set; }

        public int UseCount { get; set; }
    }

    public record QueryHandler(ClemBotContext _context) : IRequestHandler<Query, IQueryResult<Model>>
    {
        public async Task<IQueryResult<Model>> Handle(Query request, CancellationToken cancellationToken)
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
                CreationDate = tag.Time.ToDateTimeUnspecified().ToLongDateString(),
                GuildId = tag.GuildId,
                UserId = tag.UserId,
                UseCount = tag.TagUses.Count
            });
        }
    }
}
