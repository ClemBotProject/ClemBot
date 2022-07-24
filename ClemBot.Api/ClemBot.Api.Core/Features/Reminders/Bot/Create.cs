using ClemBot.Api.Common;
using ClemBot.Api.Data.Contexts;
using ClemBot.Api.Data.Models;
using FluentValidation;

namespace ClemBot.Api.Core.Features.Reminders.Bot;

public class Create
{

    public class Validator : AbstractValidator<Model>
    {
        public Validator()
        {
            RuleFor(p => p.Time).NotNull();
            RuleFor(p => p.MessageId).NotNull();
            RuleFor(p => p.UserId).NotNull();
        }
    }

    public class ReminderDto : IResponseModel
    {
        public int Id { get; set; }

        public string? Content { get; set; }

        public DateTime Time { get; set; }
    }

    public class Model : IRequest<IQueryResult<ReminderDto>>
    {
        public string Link { get; set; } = null!;

        public string? Content { get; set; }

        public DateTime Time { get; set; }

        public ulong MessageId { get; set; }

        public ulong UserId { get; set; }
    }

    public class Handler : IRequestHandler<Model, IQueryResult<ReminderDto>>
    {
        private readonly ClemBotContext _context;

        public Handler(ClemBotContext context)
        {
            _context = context;
        }

        public async Task<IQueryResult<ReminderDto>> Handle(Model request, CancellationToken cancellationToken)
        {
            var reminder = new Reminder
            {
                Link = request.Link,
                Content = request.Content,
                Time = request.Time,
                MessageId = request.MessageId,
                UserId = request.UserId
            };

            _context.Reminders.Add(reminder);
            await _context.SaveChangesAsync();

            return QueryResult<ReminderDto>.Success(new ReminderDto
            {
                Id = reminder.Id,
                Content = reminder.Content,
                Time = request.Time
            });
        }
    }
}
