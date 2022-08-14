using ClemBot.Api.Common;
using ClemBot.Api.Data.Contexts;
using FluentValidation;
using Microsoft.EntityFrameworkCore;
using NodaTime;

namespace ClemBot.Api.Core.Features.Users.Bot;

public class Reminders
{
    public class Validator : AbstractValidator<Query>
    {
        public Validator()
        {
            RuleFor(q => q.UserId).NotNull();
        }
    }

    public class ReminderDto : IResponseModel
    {
        public int Id { get; set; }

        public string Link { get; set; } = null!;

        public string? Content { get; set; }

        public LocalDateTime Time { get; set; }

        public bool Dispatched { get; set; }

        public ulong UserId { get; set; }
    }

    public class Query : IRequest<QueryResult<List<ReminderDto>>>
    {
        public ulong UserId { get; set; }
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
            if (!await _context.Users.AnyAsync(u => u.Id == request.UserId))
            {
                return QueryResult<List<ReminderDto>>.NotFound();
            }

            var reminders = await _context.Reminders
                .Where(r => r.UserId == request.UserId && !r.Dispatched)
                .Select(item => new ReminderDto
                {
                    Id = item.Id,
                    Link = item.Link,
                    Content = item.Content,
                    Time = item.Time,
                    Dispatched = item.Dispatched,
                    UserId = item.UserId
                })
                .ToListAsync();

            return QueryResult<List<ReminderDto>>.Success(reminders);
        }
    }
}
