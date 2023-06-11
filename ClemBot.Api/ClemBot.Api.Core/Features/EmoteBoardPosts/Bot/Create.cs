using ClemBot.Api.Data.Contexts;
using FluentValidation;

namespace ClemBot.Api.Core.Features.EmoteBoardPosts.Bot;

public class Create
{
    public class Validator : AbstractValidator<Command>
    {
        public Validator()
        {

        }
    }

    public class Command : IRequest<QueryResult<Unit>>
    {

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
