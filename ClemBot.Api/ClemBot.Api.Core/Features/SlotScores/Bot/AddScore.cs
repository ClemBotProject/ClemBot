using System;
using System.Threading;
using System.Threading.Tasks;
using ClemBot.Api.Common.Utilities;
using ClemBot.Api.Data.Contexts;
using ClemBot.Api.Data.Models;
using MediatR;
using NodaTime;
using NodaTime.Extensions;

namespace ClemBot.Api.Core.Features.Commands.Bot;

public class AddScore
{
    public class Command : IRequest<IQueryResult<int>>
    {
        public ulong Score { get; set; }

        public ulong GuildId { get; set; }

        public ulong UserId { get; set; }
    }

    public record Handler(ClemBotContext _context, IMediator _mediator)
        : IRequestHandler<Command, IQueryResult<int>>
    {
        public async Task<IQueryResult<int>> Handle(Command request, CancellationToken cancellationToken)
        {
            var score = new SlotScore
            {
                Score = request.Score,
                GuildId = request.GuildId,
                UserId = request.UserId,
                Time = SystemClock.Instance.InZone(DateTimeZone.Utc).GetCurrentLocalDateTime(),
            };

            _context.SlotScores.Add(score);

            await _context.SaveChangesAsync();

            return QueryResult<int>.Success(score.Id);

        }
    }
}
