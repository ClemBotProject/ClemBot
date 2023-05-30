using ClemBot.Api.Data.Contexts;
using ClemBot.Api.Services.Caching.Channels.Models;
using ClemBot.Api.Services.Caching.EmoteBoards.Models;
using ClemBot.Api.Services.Caching.Guilds.Models;
using FluentValidation;
using Microsoft.EntityFrameworkCore;

namespace ClemBot.Api.Core.Features.EmoteBoards.Bot;

public class Edit
{
    public class Validator : AbstractValidator<Command>
    {
        public Validator()
        {
            RuleFor(c => c.GuildId).NotNull();
            RuleFor(c => c.Name).NotNull().NotEmpty().Must(c => !c.Any(char.IsWhiteSpace));
            RuleFor(c => c.Emote).NotNull().NotEmpty().Must(c => !c.Any(char.IsWhiteSpace));
            RuleFor(c => c.ReactionThreshold).NotNull().Must(t => t > 0);
            RuleFor(c => c.AllowBotPosts).NotNull();
            RuleFor(c => c.Channels).NotNull();
        }
    }

    public class Command : IRequest<QueryResult<Unit>>
    {
        public ulong GuildId { get; set; }

        public string Name { get; set; } = null!;

        public string Emote { get; set; } = null!;

        public uint ReactionThreshold { get; set; }

        public bool AllowBotPosts { get; set; }

        public List<ulong> Channels { get; set; } = null!;
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

            foreach (var channelId in request.Channels)
            {
                var channelExists = await _mediator.Send(new ChannelExistsRequest
                {
                    Id = channelId
                });

                if (!channelExists)
                {
                    return QueryResult<Unit>.NotFound();
                }
            }

            // this is where caching the boards in a guild comes in handy
            var boards = await _mediator.Send(new GetEmoteBoardsRequest
            {
                GuildId = request.GuildId
            });

            var emoteBoard = boards.FirstOrDefault(b => string.Equals(b.Name, request.Name, StringComparison.OrdinalIgnoreCase));

            if (emoteBoard is null)
            {
                return QueryResult<Unit>.NotFound();
            }

            // check for emote conflicts within the guild
            var similar = boards
                .Any(b => b.Id != emoteBoard.Id && string.Equals(b.Emote, request.Emote, StringComparison.OrdinalIgnoreCase));

            if (similar)
            {
                return QueryResult<Unit>.Conflict();
            }

            emoteBoard.Emote = request.Emote;
            emoteBoard.ReactionThreshold = request.ReactionThreshold;
            emoteBoard.AllowBotPosts = request.AllowBotPosts;

            var channels = await _context.Channels
                .Where(c => request.Channels.Contains(c.Id))
                .ToListAsync();

            emoteBoard.Channels = channels;

            await _context.SaveChangesAsync();

            await _mediator.Send(new ClearEmoteBoardsRequest
            {
                GuildId = request.GuildId
            });

            return QueryResult<Unit>.NoContent();
        }
    }
}
