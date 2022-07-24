using ClemBot.Api.Data.Contexts;
using ClemBot.Api.Data.Models;
using FluentValidation;
using Microsoft.EntityFrameworkCore;

namespace ClemBot.Api.Core.Features.Reminders.Bot;

public class Details
{

    public class Validator : AbstractValidator<Query>
    {
        public Validator()
        {
            RuleFor(q => q.Id).NotNull();
        }
    }

    public class Query : IRequest<IQueryResult<Reminder>>
    {
        public int Id { get; set; }
    }

    public class Handler : IRequestHandler<Query, IQueryResult<Reminder>>
    {

        private readonly ClemBotContext _context;

        public Handler(ClemBotContext context)
        {
            _context = context;
        }

        public async Task<IQueryResult<Reminder>> Handle(Query request, CancellationToken cancellationToken)
        {
            var reminder = await _context.Reminders
                .Where(r => r.Id == request.Id)
                .FirstOrDefaultAsync();

            if (reminder is null)
            {
                return QueryResult<Reminder>.NotFound();
            }

            return QueryResult<Reminder>.Success(reminder);
        }
    }
}
