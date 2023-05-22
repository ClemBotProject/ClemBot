using ClemBot.Api.Data.Contexts;
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
            RuleFor(c => c.Id).NotNull();
            RuleFor(c => c.GuildId).NotNull();
            RuleFor(c => c.Name).NotNull().NotEmpty();
            RuleFor(c => c.Emote).NotNull().NotEmpty();
            RuleFor(c => c.ReactionThreshold).NotNull().Must(t => t > 0);
            RuleFor(c => c.AllowBotPosts).NotNull();
            RuleFor(c => c.Channels).NotNull().Must(l => l.Count > 0);
            RuleForEach(c => c.Channels).NotNull().Must(channel => channel > 0);
        }
    }

    public class Command : IRequest<QueryResult<Unit>>
    {
        public int Id { get; set; }

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

            var similar = _context.EmoteBoards
                .Any(board => board.Id != request.Id && board.GuildId == request.GuildId
                              && (string.Equals(board.Name, request.Name, StringComparison.OrdinalIgnoreCase)
                                  || string.Equals(board.Emote, request.Emote, StringComparison.OrdinalIgnoreCase)));

            if (similar)
            {
                return QueryResult<Unit>.Conflict();
            }

            var emoteBoard = await _context.EmoteBoards
                .Where(b => b.Id == request.Id)
                .FirstOrDefaultAsync();

            if (emoteBoard is null)
            {
                return QueryResult<Unit>.NotFound();
            }

            emoteBoard.Name = request.Name;
            emoteBoard.Emote = request.Emote;
            emoteBoard.ReactionThreshold = request.ReactionThreshold;
            emoteBoard.AllowBotPosts = request.AllowBotPosts;

            


            return QueryResult<Unit>.NoContent();
        }
    }
}
