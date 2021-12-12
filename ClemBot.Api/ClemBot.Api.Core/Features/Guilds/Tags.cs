using System.Collections.Generic;
using System.Linq;
using System.Threading;
using System.Threading.Tasks;
using ClemBot.Api.Common;
using ClemBot.Api.Common.Security.Policies.GuildSandbox;
using ClemBot.Api.Common.Utilities;
using ClemBot.Api.Data.Contexts;
using MediatR;
using Microsoft.EntityFrameworkCore;

namespace ClemBot.Api.Core.Features.Guilds.Bot;

public class Tags
{
    public class Query : IGuildSandboxModel, IRequest<IQueryResult<IResponseModel>>
    {
        public ulong GuildId { get; init; }
    }

    public class Tag
    {
        public string Name { get; init; } = null!;

        public string Content { get; init; } = null!;

        public string CreationDate { get; init; } = null!;

        public ulong GuildId { get; init; }

        public ulong UserId { get; init; }

        public int UseCount { get; init; }
    }

    public class Model : IResponseModel
    {
        public IEnumerable<Tag> Tags { get; init; } = null!;
    }

    public record QueryHandler(ClemBotContext _context)
        : IRequestHandler<Query, IQueryResult<IResponseModel>>
    {
        public async Task<IQueryResult<IResponseModel>> Handle(Query request,
            CancellationToken cancellationToken)
        {
            var tags = await _context.Tags
                .Where(x => x.GuildId == request.GuildId)
                .Include(y => y.TagUses)
                .ToListAsync();

            if (tags is null)
            {
                return QueryResult<IResponseModel>.NotFound();
            }

            return QueryResult<IResponseModel>.Success(new Model{ Tags = tags
                .Select(tag => new Tag
                {
                    Name = tag.Name,
                    Content = tag.Content,
                    CreationDate = tag.Time.ToDateTimeUnspecified().ToLongDateString(),
                    UserId = tag.UserId,
                    GuildId = tag.GuildId,
                    UseCount = tag.TagUses.Count
                })
            });
        }
    }
}
