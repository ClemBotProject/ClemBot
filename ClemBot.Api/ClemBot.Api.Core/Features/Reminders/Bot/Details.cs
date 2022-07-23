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

    public record Handler(ClemBotContext _context) : IRequestHandler<Query, IQueryResult<Reminder>>
    {
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
