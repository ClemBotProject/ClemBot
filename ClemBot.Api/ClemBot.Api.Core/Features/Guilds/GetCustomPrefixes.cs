using ClemBot.Api.Common;
using ClemBot.Api.Common.Security.Policies.GuildSandbox;
using ClemBot.Api.Common.Utilities;
using ClemBot.Api.Core.Behaviors;
using ClemBot.Api.Data.Contexts;
using ClemBot.Api.Services.CustomPrefix.Models;

namespace ClemBot.Api.Core.Features.Guilds;

public class GetCustomPrefixes
{
    public class Query : IGuildSandboxModel, IRequest<IQueryResult<IResponseModel>>
    {
        public ulong GuildId { get; init; }
    }

    public class Model : IResponseModel
    {
        public IEnumerable<string>? Prefixes { get; set; }
    }

    public record QueryHandler(ClemBotContext _context, IMediator _mediator)
        : IRequestHandler<Query, IQueryResult<IResponseModel>>
    {
        public async Task<IQueryResult<IResponseModel>> Handle(Query request,
            CancellationToken cancellationToken)
        {
            var prefixes = await _mediator.Send(new GetCustomPrefixRequest { Id = request.GuildId });

            return QueryResult<IResponseModel>.Success(new Model{Prefixes = prefixes});
        }
    }
}
