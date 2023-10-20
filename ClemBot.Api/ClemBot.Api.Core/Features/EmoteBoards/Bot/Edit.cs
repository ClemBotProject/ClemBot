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

        public required string Name { get; set; }

        public required string Emote { get; set; }

        public uint ReactionThreshold { get; set; }

        public bool AllowBotPosts { get; set; }

        public required List<ulong> Channels { get; set; }
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

            var board = await _context.EmoteBoards
                .Include(b => b.Channels)
                .FirstOrDefaultAsync(b => b.GuildId == request.GuildId && b.Name == request.Name);

            if (board is null)
            {
                return QueryResult<Unit>.NotFound();
            }

            // if the emote is being changed, invalidate the guild boards cache
            if (!string.Equals(request.Emote, board.Emote, StringComparison.OrdinalIgnoreCase))
            {
                await _mediator.Send(new ClearGuildBoardsRequest
                {
                    GuildId = request.GuildId
                });
            }

            board.Emote = request.Emote;
            board.ReactionThreshold = request.ReactionThreshold;
            board.AllowBotPosts = request.AllowBotPosts;

            var channels = await _context.Channels
                .Where(c => request.Channels.Contains(c.Id))
                .ToListAsync();

            board.Channels = channels;

            await _context.SaveChangesAsync();

            return QueryResult<Unit>.NoContent();
        }
    }
}
