using ClemBot.Api.Services.Caching.EmoteBoards.Models;
using ClemBot.Api.Services.Caching.Guilds.Models;
using FluentValidation;

namespace ClemBot.Api.Core.Features.EmoteBoards.Bot;

public class Index
{

    public class Validator : AbstractValidator<Query>
    {
        public Validator()
        {
            RuleFor(q => q.GuildId).NotNull();
        }
    }

    public class Query : IRequest<QueryResult<Dictionary<string, string>>>
    {
        public ulong GuildId { get; set; }
    }

    public class Handler : IRequestHandler<Query, QueryResult<Dictionary<string, string>>>
    {

        private readonly IMediator _mediator;

        public Handler(IMediator mediator)
        {
            _mediator = mediator;
        }

        public async Task<QueryResult<Dictionary<string, string>>> Handle(Query request, CancellationToken cancellationToken)
        {
            var guildExists = await _mediator.Send(new GuildExistsRequest
            {
                Id = request.GuildId
            });

            if (!guildExists)
            {
                return QueryResult<Dictionary<string, string>>.NotFound();
            }

            var boards = await _mediator.Send(new GetGuildBoardsRequest
            {
                GuildId = request.GuildId
            });

            return QueryResult<Dictionary<string, string>>.Success(boards);
        }
    }
}
