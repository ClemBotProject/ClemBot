using ClemBot.Api.Common;
using ClemBot.Api.Data.Contexts;
using ClemBot.Api.Services.Caching.EmoteBoards.Models;
using ClemBot.Api.Services.Caching.Guilds.Models;
using FluentValidation;

namespace ClemBot.Api.Core.Features.EmoteBoardPosts.Bot;

public class Index
{
    public class Validator : AbstractValidator<Query>
    {
        public Validator()
        {
            RuleFor(q => q.GuildId).NotNull();
            RuleFor(q => q.Name).NotNull().NotEmpty().Must(s => !s.Any(char.IsWhiteSpace));
        }
    }

    public class EmoteBoardPostDto : IResponseModel
    {
        public ulong UserId { get; init; }

        public ulong MessageId { get; init; }

        public ulong ChannelId { get; init; }

        public List<ulong> Reactions { get; init; } = null!;
    }

    public class Query : IRequest<QueryResult<List<EmoteBoardPostDto>>>
    {
        public ulong GuildId { get; set; }

        public required string Name { get; set; }
    }

    public class Handler : IRequestHandler<Query, QueryResult<List<EmoteBoardPostDto>>>
    {
        private readonly IMediator _mediator;
        private readonly ClemBotContext _context;

        public Handler(IMediator mediator, ClemBotContext context)
        {
            _mediator = mediator;
            _context = context;
        }

        public async Task<QueryResult<List<EmoteBoardPostDto>>> Handle(Query query, CancellationToken token)
        {
            var guildExists = await _mediator.Send(new GuildExistsRequest
            {
                Id = query.GuildId
            });

            if (!guildExists)
            {
                return QueryResult<List<EmoteBoardPostDto>>.NotFound();
            }

            var boards = await _mediator.Send(new GetEmoteBoardsRequest
            {
                GuildId = query.GuildId
            });

            var board = boards.FirstOrDefault(b => string.Equals(b.Name, query.Name, StringComparison.OrdinalIgnoreCase));

            if (board is null)
            {
                return QueryResult<List<EmoteBoardPostDto>>.NotFound();
            }

            // todo

            return QueryResult<List<EmoteBoardPostDto>>.NoContent();
        }
    }
}
