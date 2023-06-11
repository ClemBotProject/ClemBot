using ClemBot.Api.Common;
using ClemBot.Api.Data.Contexts;
using FluentValidation;

namespace ClemBot.Api.Core.Features.EmoteBoardPosts.Bot.Leaderboard;

/// <summary>
/// This route returns a leaderboard categorized by how many reactions a single post received.
/// </summary>
public class Popular
{
    public class Validator : AbstractValidator<Query>
    {
        public Validator()
        {
            RuleFor(q => q.GuildId).NotNull();
        }
    }

    public class LeaderboardSlot : IResponseModel
    {
        public ulong UserId { get; init; }

        public ulong ChannelId { get; init; }

        public ulong MessageId { get; init; }

        public int ReactionCount { get; init; }

        public required string Emote { get; init; }
    }

    public class Query : IRequest<QueryResult<List<LeaderboardSlot>>>
    {
        public ulong GuildId { get; set; }

        public string? Name { get; set; }
    }

    public class Handler : IRequestHandler<Query, QueryResult<List<LeaderboardSlot>>>
    {

        private readonly IMediator _mediator;
        private readonly ClemBotContext _context;

        public Handler(IMediator mediator, ClemBotContext context)
        {
            _mediator = mediator;
            _context = context;
        }

        public async Task<QueryResult<List<LeaderboardSlot>>> Handle(Query request, CancellationToken cancellationToken)
        {
            return QueryResult<List<LeaderboardSlot>>.NoContent();
        }
    }
}
