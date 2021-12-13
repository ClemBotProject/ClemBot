using System;
using System.Linq;
using System.Threading;
using System.Threading.Tasks;
using ClemBot.Api.Common.Enums;
using ClemBot.Api.Common.Utilities;
using ClemBot.Api.Data.Contexts;
using MediatR;
using Microsoft.EntityFrameworkCore;
using NodaTime;

namespace ClemBot.Api.Core.Features.Infractions.Bot;

public class Details
{
    public class Query : IRequest<IQueryResult<Model>>
    {
        public int Id { get; set; }
    }

    public class Model
    {
        public ulong GuildId { get; set; }

        public ulong AuthorId { get; set; }

        public ulong SubjectId { get; set; }

        public InfractionType Type { get; set; }

        public string? Reason { get; set; }

        public LocalDateTime? Duration { get; set; }

        public LocalDateTime Time { get; set; }

        public bool? Active { get; set; }
    }

    public record QueryHandler(ClemBotContext _context) : IRequestHandler<Query, IQueryResult<Model>>
    {
        public async Task<IQueryResult<Model>> Handle(Query request, CancellationToken cancellationToken)
        {
            var infraction = await _context.Infractions.FirstOrDefaultAsync(y => y.Id == request.Id);

            if (infraction is null)
            {
                return QueryResult<Model>.NotFound();
            }

            return QueryResult<Model>.Success(new Model()
            {
                GuildId = infraction.GuildId,
                AuthorId = infraction.AuthorId,
                SubjectId = infraction.SubjectId,
                Reason = infraction.Reason,
                Duration = infraction.Duration,
                Time = infraction.Time,
                Type = infraction.Type,
                Active = infraction.IsActive
            });
        }
    }
}
