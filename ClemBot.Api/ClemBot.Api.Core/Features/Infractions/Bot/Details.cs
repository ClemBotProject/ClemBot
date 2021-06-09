using System;
using System.Linq;
using System.Threading;
using System.Threading.Tasks;
using ClemBot.Api.Core.Utilities;
using ClemBot.Api.Data.Contexts;
using ClemBot.Api.Data.Enums;
using MediatR;
using Microsoft.EntityFrameworkCore;

namespace ClemBot.Api.Core.Features.Infractions.Bot
{
    public class Details
    {
        public class Query : IRequest<Result<Model, QueryStatus>>
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

            public DateTime? Duration { get; set; }

            public DateTime Time { get; set; }

            public bool? Active { get; set; }
        }

        public record QueryHandler(ClemBotContext _context) : IRequestHandler<Query, Result<Model, QueryStatus>>
        {
            public async Task<Result<Model, QueryStatus>> Handle(Query request, CancellationToken cancellationToken)
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
}
