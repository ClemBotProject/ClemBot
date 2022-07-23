using ClemBot.Api.Common;
using ClemBot.Api.Data.Contexts;
using FluentValidation;
using Microsoft.EntityFrameworkCore;

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

        public DateTime Time { get; set; }

        public ulong MessageId { get; set; }

        public ulong UserId { get; set; }
    }

    public class Query : IRequest<IQueryResult<List<ReminderDto>>>
    {
        public ulong UserId { get; set; }
    }

    public record Handler(ClemBotContext _context) : IRequestHandler<Query, IQueryResult<List<ReminderDto>>>
    {
        public async Task<IQueryResult<List<ReminderDto>>> Handle(Query request, CancellationToken cancellationToken)
        {
            var reminders = await _context.Reminders
                .Where(r => r.UserId == request.UserId && !r.Dispatched)
                .Select(item => new ReminderDto
                {
                    Id = item.Id,
                    Link = item.Link,
                    Content = item.Content,
                    Time = item.Time,
                    MessageId = item.MessageId,
                    UserId = item.UserId
                })
                .ToListAsync();

            return QueryResult<List<ReminderDto>>.Success(reminders);
        }
    }
}
