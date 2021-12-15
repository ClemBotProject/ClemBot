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

public class AddInvocation
{
    public class Command : IRequest<IQueryResult<int>>
    {
        public string CommandName { get; set; } = null!;

        public ulong GuildId { get; set; }

        public ulong ChannelId { get; set; }

        public ulong UserId { get; set; }
    }

    public record Handler(ClemBotContext _context, IMediator _mediator)
        : IRequestHandler<Command, IQueryResult<int>>
    {
        public async Task<IQueryResult<int>> Handle(Command request, CancellationToken cancellationToken)
        {
            var invocationEntity = new CommandInvocation
            {
                CommandName = request.CommandName,
                Time = SystemClock.Instance.InZone(DateTimeZone.Utc).GetCurrentLocalDateTime(),
                GuildId = request.GuildId,
                ChannelId = request.ChannelId,
                UserId = request.UserId
            };

            _context.CommandInvocations.Add(invocationEntity);

            await _context.SaveChangesAsync();

            return QueryResult<int>.Success(invocationEntity.Id);
        }
    }
}
