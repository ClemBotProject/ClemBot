using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading;
using System.Threading.Tasks;
using ClemBot.Api.Core.Utilities;
using ClemBot.Api.Data.Contexts;
using ClemBot.Api.Data.Enums;
using MediatR;
using Microsoft.EntityFrameworkCore;

namespace ClemBot.Api.Core.Features.Guilds.Bot
{
    public class Infractions
    {
        public class Query : IRequest<Result<IEnumerable<Model>, QueryStatus>>
        {
            public ulong Id { get; init; }
        }

        public class Model
        {
            public int Id { get; set; }

            public ulong GuildId { get; set; }

            public ulong AuthorId { get; set; }

            public ulong SubjectId { get; set; }

            public InfractionType Type { get; set; }

            public string? Reason { get; set; }

            public DateTime? Duration { get; set; }

            public DateTime Time { get; set; }

            public bool? Active { get; set; }
        }


        public record QueryHandler(ClemBotContext _context)
            : IRequestHandler<Query, Result<IEnumerable<Model>, QueryStatus>>
        {
            public async Task<Result<IEnumerable<Model>, QueryStatus>> Handle(Query request,
                CancellationToken cancellationToken)
            {
                var infractions = await _context.Infractions
                    .Where(x => x.GuildId == request.Id)
                    .ToListAsync();

                if (infractions is null)
                {
                    return QueryResult<IEnumerable<Model>>.NotFound();
                }

                return QueryResult<IEnumerable<Model>>.Success(infractions
                    .Select(y => new Model
                    {
                        Id = y.Id,
                        GuildId = y.GuildId,
                        AuthorId = y.AuthorId,
                        SubjectId = y.SubjectId,
                        Reason = y.Reason,
                        Duration = y.Duration,
                        Time = y.Time,
                        Type = y.Type,
                        Active = y.IsActive
                    }));
            }
        }
    }
}
