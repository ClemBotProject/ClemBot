using System;
using System.Threading;
using System.Threading.Tasks;
using ClemBot.Api.Common.Enums;
using ClemBot.Api.Common.Utilities;
using ClemBot.Api.Data.Contexts;
using ClemBot.Api.Data.Models;
using FluentValidation;
using MediatR;
using NodaTime;
using NodaTime.Extensions;

namespace ClemBot.Api.Core.Features.Infractions.Bot;

public class Create
{
    public class Validator : AbstractValidator<Command>
    {
        public Validator()
        {
            RuleFor(p => p.GuildId).NotNull();
            RuleFor(p => p.SubjectId).NotNull();
            RuleFor(p => p.AuthorId).NotNull();
            RuleFor(p => p.Type).NotNull();
        }
    }

    public class InfractionDto
    {
        public ulong GuildId { get; set; }

        public int InfractionId { get; set; }

        public InfractionType Type { get; set; }
    }

    public class Command : IRequest<IQueryResult<InfractionDto>>
    {
        public ulong GuildId { get; set; }

        public ulong AuthorId { get; set; }

        public ulong SubjectId { get; set; }

        public InfractionType Type { get; set; }

        public string? Reason { get; set; }

        public LocalDateTime? Duration { get; set; }

        public bool? Active { get; set; }
    }

    public record Handler(ClemBotContext _context) : IRequestHandler<Command, IQueryResult<InfractionDto>>
    {
        public async Task<IQueryResult<InfractionDto>> Handle(Command request, CancellationToken cancellationToken)
        {
            var infraction = new Infraction()
            {
                GuildId = request.GuildId,
                AuthorId = request.AuthorId,
                SubjectId = request.SubjectId,
                Reason = request.Reason,
                Duration = request.Duration,
                Time = SystemClock.Instance.InZone(DateTimeZone.Utc).GetCurrentLocalDateTime(),
                Type = request.Type,
                IsActive = request.Active
            };

            _context.Infractions.Add(infraction);
            await _context.SaveChangesAsync();

            return QueryResult<InfractionDto>.Success(new InfractionDto()
            {
                GuildId = infraction.GuildId,
                InfractionId = infraction.Id,
                Type = infraction.Type
            });
        }
    }
}
