using ClemBot.Api.Common;
using ClemBot.Api.Data.Contexts;
using FluentValidation;

namespace ClemBot.Api.Core.Features.EmoteBoards.Bot;

public class Delete
{

    public class Validator : AbstractValidator<Command>
    {
        public Validator()
        {
            RuleFor(c => c.Id).NotNull();
            RuleFor(c => c.GuildId).NotNull();
        }
    }

    public class Command : IRequest<QueryResult<Unit>>
    {
        public int Id { get; set; }

        public ulong GuildId { get; set; }
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
            return QueryResult<Unit>.NoContent();
        }
    }
}
