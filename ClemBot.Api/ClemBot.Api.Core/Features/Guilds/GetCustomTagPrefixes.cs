using ClemBot.Api.Common;
using ClemBot.Api.Common.Security.Policies.GuildSandbox;
using ClemBot.Api.Data.Contexts;
using ClemBot.Api.Services.Caching.CustomTagPrefix.Models;

namespace ClemBot.Api.Core.Features.Guilds;

public class GetCustomTagPrefixes
{
    public class Query : IGuildSandboxModel, IRequest<IQueryResult<Model>>
    {
        public ulong GuildId { get; init; }
    }

    public class Model : IResponseModel
    {
        public IEnumerable<string>? TagPrefixes { get; set; }
    }

    public record QueryHandler(ClemBotContext _context, IMediator _mediator)
        : IRequestHandler<Query, IQueryResult<Model>>
    {
        public async Task<IQueryResult<Model>> Handle(Query request,
            CancellationToken cancellationToken)
        {
            var tagprefixes = await _mediator.Send(new GetCustomTagPrefixRequest { Id = request.GuildId });

            return QueryResult<Model>.Success(new Model{ TagPrefixes = tagprefixes });
        }
    }
}
