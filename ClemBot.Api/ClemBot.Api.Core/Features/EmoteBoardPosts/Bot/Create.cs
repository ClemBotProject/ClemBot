using ClemBot.Api.Data.Contexts;
using ClemBot.Api.Data.Models;
using ClemBot.Api.Services.Caching.Channels.Models;
using ClemBot.Api.Services.Caching.EmoteBoardPosts.Models;
using ClemBot.Api.Services.Caching.EmoteBoards.Models;
using ClemBot.Api.Services.Caching.Guilds.Models;
using ClemBot.Api.Services.Caching.Messages.Models;
using ClemBot.Api.Services.Caching.Users.Models;
using FluentValidation;

namespace ClemBot.Api.Core.Features.EmoteBoardPosts.Bot;

public class Create
{
    public class Validator : AbstractValidator<Command>
    {
        public Validator()
        {
            RuleFor(c => c.GuildId).NotNull();
            RuleFor(c => c.Name).NotNull().NotEmpty().Must(s => !s.Any(char.IsWhiteSpace));
            RuleFor(c => c.ChannelId).NotNull();
            RuleFor(c => c.MessageId).NotNull();
            RuleFor(c => c.UserId).NotNull();
            RuleFor(c => c.Reactions).NotNull().NotEmpty();
            RuleFor(c => c.MessageIds).NotNull().NotEmpty();
        }
    }

    public class Command : IRequest<QueryResult<Unit>>
    {
        public ulong GuildId { get; set; }

        public required string Name { get; set; }

        public ulong ChannelId { get; set; }

        public ulong MessageId { get; set; }

        public ulong UserId { get; set; }

        public required List<ulong> Reactions { get; set; }

        public required Dictionary<ulong, ulong> MessageIds { get; set; }
    }

    public class Handler : IRequestHandler<Command, QueryResult<Unit>>
    {

        private readonly IMediator _mediator;
        private readonly ClemBotContext _context;

        public Handler(IMediator mediator, ClemBotContext context)
        {
            _mediator = mediator;
            _context = context;
        }

        public async Task<QueryResult<Unit>> Handle(Command request, CancellationToken cancellationToken)
        {
            var guildExists = await _mediator.Send(new GuildExistsRequest
            {
                Id = request.GuildId
            });

            if (!guildExists)
            {
                return QueryResult<Unit>.NotFound();
            }

            var channelExists = await _mediator.Send(new ChannelExistsRequest
            {
                Id = request.ChannelId
            });

            if (!channelExists)
            {
                return QueryResult<Unit>.NotFound();
            }

            var messageExists = await _mediator.Send(new MessageExistsRequest
            {
                Id = request.MessageId
            });

            if (!messageExists)
            {
                return QueryResult<Unit>.NotFound();
            }

            var userExists = await _mediator.Send(new UserExistsRequest
            {
                Id = request.UserId
            });

            if (!userExists)
            {
                return QueryResult<Unit>.NotFound();
            }

            var boards = await _mediator.Send(new GetEmoteBoardsRequest
            {
                GuildId = request.GuildId
            });

            var board = boards.FirstOrDefault(b => string.Equals(b.Name, request.Name, StringComparison.OrdinalIgnoreCase));

            if (board is null)
            {
                return QueryResult<Unit>.NotFound();
            }

            if (board.ReactionThreshold > request.Reactions.Count)
            {
                return QueryResult<Unit>.Conflict();
            }

            var postExists = await _mediator.Send(new EmoteBoardPostExistsRequest
            {
                BoardId = board.Id,
                MessageId = request.MessageId
            });

            if (postExists)
            {
                return QueryResult<Unit>.Conflict();
            }

            var messages = request.MessageIds.Select(kvp => new EmoteBoardMessage
            {
                EmoteBoardPostId = board.Id,
                ChannelId = kvp.Key,
                MessageId = kvp.Value
            }).ToList();

            _context.EmoteBoardPosts.Add(new EmoteBoardPost
            {
                EmoteBoardId = board.Id,
                ChannelId = request.ChannelId,
                MessageId = request.MessageId,
                UserId = request.UserId,
                Reactions = request.Reactions,
                Messages = messages
            });
            await _context.SaveChangesAsync();

            await _mediator.Send(new ClearEmoteBoardPostRequest
            {
                BoardId = board.Id, MessageId = request.MessageId
            });

            return QueryResult<Unit>.NoContent();
        }
    }
}
