using ClemBot.Api.Common;
using ClemBot.Api.Data.Contexts;
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

    public class EmoteBoardDto : IResponseModel
    {
        public ulong GuildId { get; init; }

        public required string Name { get; init; }

        public required string Emote { get; init; }

        public uint ReactionThreshold { get; init; }

        public bool AllowBotPosts { get; init; }

        public required List<ulong> Channels { get; init; }
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

            var boards = await _mediator.Send(new GetEmoteBoardsRequest
            {
                GuildId = request.GuildId
            });

            var dtos = boards.Select(board => new EmoteBoardDto
            {
                GuildId = board.GuildId,
                Name = board.Name,
                Emote = board.Emote,
                ReactionThreshold = board.ReactionThreshold,
                AllowBotPosts = board.AllowBotPosts,
                Channels = board.Channels.Select(c => c.Id).ToList()
            }).ToList();

            return QueryResult<List<EmoteBoardDto>>.Success(dtos);
        }
    }
}
