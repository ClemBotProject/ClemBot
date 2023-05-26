using ClemBot.Api.Common;
using ClemBot.Api.Data.Contexts;
using FluentValidation;

namespace ClemBot.Api.Core.Features.EmoteBoardPosts.Bot;

public class Index
{
    public class Validator : AbstractValidator<Query>
    {
        public Validator()
        {

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
        public int EmoteBoardId { get; set; }

        public ulong GuildId { get; set; }
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
            return QueryResult<List<EmoteBoardPostDto>>.NoContent();
        }
    }
}
