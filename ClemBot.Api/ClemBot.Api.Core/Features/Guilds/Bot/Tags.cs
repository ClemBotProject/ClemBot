using System.Collections.Generic;
using System.Linq;
using System.Threading;
using System.Threading.Tasks;
using ClemBot.Api.Common.Utilities;
using ClemBot.Api.Data.Contexts;
using MediatR;
using Microsoft.EntityFrameworkCore;

namespace ClemBot.Api.Core.Features.Guilds.Bot;

public class Tags
{
    public class Query : IRequest<IQueryResult<IEnumerable<Model>>>
    {
        public ulong Id { get; init; }
    }

    public class Model
    {
        public string Name { get; init; } = null!;

        public string Content { get; init; } = null!;

        public string CreationDate { get; init; } = null!;

        public ulong GuildId { get; init; }

        public ulong UserId { get; init; }

        public int UseCount { get; init; }
    }

    public record QueryHandler(ClemBotContext _context)
        : IRequestHandler<Query, IQueryResult<IEnumerable<Model>>>
    {
        public async Task<IQueryResult<IEnumerable<Model>>> Handle(Query request,
            CancellationToken cancellationToken)
        {
            var tags = await _context.Tags
                .Where(x => x.GuildId == request.Id)
                .Include(y => y.TagUses)
                .ToListAsync();

            if (tags is null)
            {
                return QueryResult<IEnumerable<Model>>.NotFound();
            }

            return QueryResult<IEnumerable<Model>>.Success(tags
                .Select(tag => new Model
                {
                    Name = tag.Name,
                    Content = tag.Content,
                    CreationDate = tag.Time.ToDateTimeUnspecified().ToLongDateString(),
                    UserId = tag.UserId,
                    GuildId = tag.GuildId,
                    UseCount = tag.TagUses.Count
                }));
        }
    }
}
