using ClemBot.Api.Common;
using ClemBot.Api.Data.Contexts;
using ClemBot.Api.Services.Caching.EmoteBoardPosts.Models;
using ClemBot.Api.Services.Caching.EmoteBoards.Models;
using ClemBot.Api.Services.Caching.Guilds.Models;
using FluentValidation;
using Microsoft.EntityFrameworkCore;

namespace ClemBot.Api.Core.Features.EmoteBoardPosts.Bot;

public class React
{
    public class Validator : AbstractValidator<Command>
    {
        public Validator()
        {
            RuleFor(c => c.GuildId).NotNull();
            RuleFor(c => c.Name).NotNull().NotEmpty().Must(s => !s.Any(char.IsWhiteSpace));
            RuleFor(c => c.MessageId).NotNull();
            RuleFor(c => c.UserReactions).NotNull().NotEmpty();
        }
    }

    public class EmoteBoardReactionDto : IResponseModel
    {
        public bool Update { get; init; }

        public int? ReactionCount { get; init; }

        public Dictionary<ulong, ulong>? Messages { get; init; }
    }

    public class Command : IRequest<QueryResult<EmoteBoardReactionDto>>
    {
        public ulong GuildId { get; set; }

        public required string Name { get; set; }

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

            var boards = await _mediator.Send(new GetEmoteBoardsRequest
            {
                GuildId = request.GuildId
            });

            var board = boards.FirstOrDefault(b => string.Equals(b.Name, request.Name, StringComparison.OrdinalIgnoreCase));

            if (board is null)
            {
                return QueryResult<EmoteBoardReactionDto>.NotFound();
            }

            var postExists = await _mediator.Send(new EmoteBoardPostExistsRequest
            {
                BoardId = board.Id,
                MessageId = request.MessageId
            });

            if (!postExists)
            {
                return QueryResult<EmoteBoardReactionDto>.NotFound();
            }

            var post = _context.EmoteBoardPosts
                .Include(p => p.Reactions)
                .Include(p => p.Messages)
                .FirstOrDefault(p => p.EmoteBoardId == board.Id && p.MessageId == request.MessageId);

            if (post is null)
            {
                return QueryResult<EmoteBoardReactionDto>.Conflict();
            }

            var newReactions = request.UserReactions.Where(id => !post.Reactions.Contains(id)).ToList();

            if (newReactions.Count == 0)
            {
                return QueryResult<EmoteBoardReactionDto>.Success(new EmoteBoardReactionDto
                {
                    Update = false
                });
            }

            post.Reactions.AddRange(newReactions);
            await _context.SaveChangesAsync();

            return QueryResult<EmoteBoardReactionDto>.Success(new EmoteBoardReactionDto
            {
                Update = true,
                ReactionCount = post.Reactions.Count,
                Messages = post.Messages.ToDictionary(message => message.ChannelId, message => message.MessageId)
            });
        }
    }
}
