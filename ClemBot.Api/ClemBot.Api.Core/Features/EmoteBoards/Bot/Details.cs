using ClemBot.Api.Common;
using ClemBot.Api.Services.Caching.EmoteBoards.Models;
using ClemBot.Api.Services.Caching.Guilds.Models;
using FluentValidation;

namespace ClemBot.Api.Core.Features.EmoteBoards.Bot;

public class Details
{
    public class Validator : AbstractValidator<Query>
    {
        public Validator()
        {
            RuleFor(q => q.GuildId).NotNull();
            RuleFor(q => q.Name).NotNull().NotEmpty().Must(s => !s.Any(char.IsWhiteSpace));
        }
    }

    public class EmoteBoardDto : IResponseModel
    {
        public required string Name { get; init; }

        public required string Emote { get; init; }

        public uint ReactionThreshold { get; init; }

        public bool AllowBotPosts { get; init; }

        public required List<ulong> Channels { get; init; }
    }

    public class Query : IRequest<QueryResult<EmoteBoardDto>>
    {
        public ulong GuildId { get; set; }

        public required string Name { get; set; }
    }

    public class Handler : IRequestHandler<Query, QueryResult<EmoteBoardDto>>
    {

        private readonly IMediator _mediator;

        public Handler(IMediator mediator)
        {
            _mediator = mediator;
        }

        public async Task<QueryResult<EmoteBoardDto>> Handle(Query request, CancellationToken cancellationToken)
        {
            var guildExists = await _mediator.Send(new GuildExistsRequest
            {
                Id = request.GuildId
            });

            if (!guildExists)
            {
                return QueryResult<EmoteBoardDto>.NotFound();
            }

            var board = await _mediator.Send(new GetEmoteBoardRequest
            {
                GuildId = request.GuildId,
                Name = request.Name
            });

            if (board is null)
            {
                return QueryResult<EmoteBoardDto>.NotFound();
            }

            var dto = new EmoteBoardDto
            {
                Name = board.Name,
                Emote = board.Emote,
                ReactionThreshold = board.ReactionThreshold,
                AllowBotPosts = board.AllowBotPosts,
                Channels = board.Channels.Select(c => c.Id).ToList()
            };

            return QueryResult<EmoteBoardDto>.Success(dto);
        }
    }
}
