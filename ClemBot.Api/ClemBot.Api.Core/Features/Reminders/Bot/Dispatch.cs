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

    public class Query : IRequest<IQueryResult<Guid>>
    {
        public int Id { get; set; }
    }

    public record Handler(ClemBotContext _context) : IRequestHandler<Query, IQueryResult<Guid>>
    {
        public async Task<IQueryResult<Guid>> Handle(Query request, CancellationToken cancellationToken)
        {
            var reminder = await _context.Reminders
                .FirstOrDefaultAsync(r => r.Id == request.Id);

            if (reminder is null)
            {
                return QueryResult<Guid>.NotFound();
            }

            if (reminder.Dispatched)
            {
                return QueryResult<Guid>.Conflict();
            }

            reminder.Dispatched = true;
            await _context.SaveChangesAsync();

            return QueryResult<Guid>.Success(reminder.TaskId);
        }
    }
}
