using ClemBot.Api.Data.Contexts;
using ClemBot.Api.Services.Caching.EmoteBoards.Models;
using ClemBot.Api.Services.Caching.Guilds.Models;
using FluentValidation;
using LinqToDB;

namespace ClemBot.Api.Core.Features.EmoteBoards.Bot;

public class Delete
{

    public class Validator : AbstractValidator<Command>
    {
        public Validator()
        {
            RuleFor(c => c.GuildId).NotNull();
            RuleFor(c => c.Name).NotNull().Must(s => !s.Any(char.IsWhiteSpace));
        }
    }

    public class Command : IRequest<QueryResult<Unit>>
    {
        public ulong GuildId { get; set; }

        public required string Name { get; set; }
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

            var board = await _context.EmoteBoards
                .FirstOrDefaultAsync(b => b.GuildId == request.GuildId && b.Name == request.Name);

            if (board is null)
            {
                return QueryResult<Unit>.NotFound();
            }

            _context.EmoteBoards.Remove(board);
            await _context.SaveChangesAsync();

            await _mediator.Send(new ClearGuildBoardsRequest
            {
                GuildId = request.GuildId
            });

            return QueryResult<Unit>.NoContent();
        }
    }
}
