using ClemBot.Api.Common;
using ClemBot.Api.Data.Contexts;
using Microsoft.EntityFrameworkCore;
using NodaTime;

namespace ClemBot.Api.Core.Features.Reminders.Bot;

public class Index
{
    public class ReminderDto : IResponseModel
    {
        public int Id { get; set; }

        public LocalDateTime Time { get; set; }
    }

    public class Query : IRequest<QueryResult<List<ReminderDto>>>
    {
        // empty
    }

    public class Handler : IRequestHandler<Query, QueryResult<List<ReminderDto>>>
    {

        private readonly ClemBotContext _context;

        public Handler(ClemBotContext context)
        {
            _context = context;
        }

        public async Task<QueryResult<List<ReminderDto>>> Handle(Query request, CancellationToken cancellationToken)
        {
            var reminders = await _context.Reminders
                .Where(r => !r.Dispatched)
                .Select(item => new ReminderDto
                {
                    Id = item.Id,
                    Time = item.Time
                })
                .ToListAsync();

            return QueryResult<List<ReminderDto>>.Success(reminders);
        }
    }
}
