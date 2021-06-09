using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading;
using System.Threading.Tasks;
using ClemBot.Api.Core.Utilities;
using ClemBot.Api.Data.Contexts;
using ClemBot.Api.Data.Enums;
using ClemBot.Api.Data.Models;
using MediatR;
using Microsoft.EntityFrameworkCore;

namespace ClemBot.Api.Core.Features.Users.Bot
{
    public class Infractions
    {
        public class Query : IRequest<Result<IEnumerable<Model>, QueryStatus>>
        {
            public ulong UserId { get; set; }

            public ulong GuildId { get; set; }

            public InfractionType? Type { get; set; } = null;
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
                    .Where(x => x.SubjectId == request.UserId && x.GuildId == request.GuildId)
                    .Where(x => request.Type == null || request.Type == x.Type)
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
                    })
                    .ToListAsync();

                return QueryResult<IEnumerable<Model>>.Success(infractions);
            }
        }
    }
}
