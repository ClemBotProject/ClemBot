using ClemBot.Api.Data.Contexts;
using ClemBot.Api.Data.Models;
using FluentValidation;
using LinqToDB;

namespace ClemBot.Api.Core.Features.Reminders.Bot;

public class Edit
{

    public class Query : IRequest<IQueryResult<int>>
    {
        public Dictionary<int, Guid> ReminderTaskIds { get; set; } = new();
    }

    public record Handler(ClemBotContext _context) : IRequestHandler<Query, IQueryResult<int>>
    {
        public async Task<IQueryResult<int>> Handle(Query request, CancellationToken cancellationToken)
        {
            var reminders = await _context.Reminders
                .Where(r => request.ReminderTaskIds.ContainsKey(r.Id))
                .ToListAsync();

            foreach (var reminder in reminders)
            {
                reminder.TaskId = request.ReminderTaskIds[reminder.Id];
            }

            await _context.SaveChangesAsync();

            return QueryResult<int>.Success(0);
        }
    }
}
