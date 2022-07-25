using ClemBot.Api.Common;
using ClemBot.Api.Data.Contexts;
using ClemBot.Api.Data.Models;
using FluentValidation;
using Microsoft.EntityFrameworkCore;
using NodaTime;

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

    public class ReminderDto : IResponseModel
    {
        public int Id { get; set; }

        public string Link { get; set; } = null!;

        public string? Content { get; set; }

        public LocalDateTime Time { get; set; }

        public ulong UserId { get; set; }
    }

    public class Query : IRequest<IQueryResult<ReminderDto>>
    {
        public int Id { get; set; }
    }

    public class Handler : IRequestHandler<Query, IQueryResult<ReminderDto>>
    {

        private readonly ClemBotContext _context;

        public Handler(ClemBotContext context)
        {
            _context = context;
        }

        public async Task<IQueryResult<ReminderDto>> Handle(Query request, CancellationToken cancellationToken)
        {
            var reminder = await _context.Reminders
                .Where(r => r.Id == request.Id)
                .Select(item => new ReminderDto
                {
                    Id = item.Id,
                    Link = item.Link,
                    Content = item.Content,
                    Time = item.Time,
                    UserId = item.UserId
                })
                .FirstOrDefaultAsync();

            if (reminder is null)
            {
                return QueryResult<ReminderDto>.NotFound();
            }

            return QueryResult<ReminderDto>.Success(reminder);
        }
    }
}
