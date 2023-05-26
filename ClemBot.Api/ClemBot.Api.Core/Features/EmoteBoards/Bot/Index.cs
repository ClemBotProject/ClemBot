using ClemBot.Api.Common;
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

    public class Query : IRequest<QueryResult<List<EmoteBoardDto>>>
    {
        public ulong GuildId { get; set; }
    }

    public class Handler : IRequestHandler<Query, QueryResult<List<EmoteBoardDto>>>
    {

        private readonly IMediator _mediator;

        public Handler(IMediator mediator)
        {
            _mediator = mediator;
        }

        public async Task<QueryResult<List<EmoteBoardDto>>> Handle(Query request, CancellationToken cancellationToken)
        {
            var guildExists = await _mediator.Send(new GuildExistsRequest
            {
                Id = request.GuildId
            });

            if (!guildExists)
            {
                return QueryResult<List<EmoteBoardDto>>.NotFound();
            }

            var emoteBoards = await _mediator.Send(new GetEmoteBoardsRequest
            {
                GuildId = request.GuildId
            });

            return QueryResult<List<EmoteBoardDto>>.Success(emoteBoards);
        }
    }
}
