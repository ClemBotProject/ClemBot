using ClemBot.Api.Common;
using ClemBot.Api.Data.Contexts;
using ClemBot.Api.Services.Caching.Guilds.Models;
using FluentValidation;

namespace ClemBot.Api.Core.Features.EmoteBoardPosts.Bot;

public class React
{
    public class Validator : AbstractValidator<Command>
    {
        public Validator()
        {
            RuleFor(c => c.GuildId).NotNull();
            RuleFor(c => c.ChannelId).NotNull();
            RuleFor(c => c.MessageId).NotNull();
            RuleFor(c => c.UserReactions).NotNull().Must(l => l.Count > 0);
        }
    }

    public class EmoteBoardReactionDto : IResponseModel
    {
        public bool Update { get; init; }

        public uint? ReactionCount { get; init; }

        public Dictionary<ulong, ulong>? Messages { get; init; }
    }

    public class Command : IRequest<QueryResult<EmoteBoardReactionDto>>
    {
        public ulong GuildId { get; set; }

        public ulong ChannelId { get; set; }

        public ulong MessageId { get; set; }

        public required List<ulong> UserReactions { get; set; }
    }

    public class Handler : IRequestHandler<Command, QueryResult<EmoteBoardReactionDto>>
    {

        private readonly IMediator _mediator;
        private readonly ClemBotContext _context;

        public Handler(IMediator mediator, ClemBotContext context)
        {
            _mediator = mediator;
            _context = context;
        }

        public async Task<QueryResult<EmoteBoardReactionDto>> Handle(Command request, CancellationToken cancellationToken)
        {
            var guildExists = await _mediator.Send(new GuildExistsRequest
            {
                Id = request.GuildId
            });

            if (!guildExists)
            {
                return QueryResult<EmoteBoardReactionDto>.NotFound();
            }

            // todo

            return QueryResult<EmoteBoardReactionDto>.NoContent();
        }
    }
}
