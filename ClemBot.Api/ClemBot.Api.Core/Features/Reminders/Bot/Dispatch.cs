using ClemBot.Api.Data.Contexts;
using FluentValidation;
using Microsoft.EntityFrameworkCore;

namespace ClemBot.Api.Core.Features.Reminders.Bot;

public class Dispatch
{

    public class Validator : AbstractValidator<Query>
    {
        public Validator()
        {
            RuleFor(q => q.Id).NotNull();
        }
    }

    public class Query : IRequest<QueryResult<int>>
    {
        public int Id { get; set; }
    }

    public class Handler : IRequestHandler<Query, QueryResult<int>>
    {

        private readonly ClemBotContext _context;

        public Handler(ClemBotContext context)
        {
            _context = context;
        }

        public async Task<QueryResult<int>> Handle(Query request, CancellationToken cancellationToken)
        {
            var reminder = await _context.Reminders
                .FirstOrDefaultAsync(r => r.Id == request.Id);

            if (reminder is null)
            {
                return QueryResult<int>.NotFound();
            }

            if (reminder.Dispatched)
            {
                return QueryResult<int>.Conflict();
            }

            reminder.Dispatched = true;
            await _context.SaveChangesAsync();

            return QueryResult<int>.Success(reminder.Id);
        }
    }
}
