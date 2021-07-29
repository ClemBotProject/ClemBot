using System;
using System.Threading;
using System.Threading.Tasks;
using ClemBot.Api.Core.Utilities;
using ClemBot.Api.Data.Contexts;
using ClemBot.Api.Data.Models;
using MediatR;

namespace ClemBot.Api.Core.Features.Commands.Bot
{
    public class AddInvocation
    {
        public class Command : IRequest<Result<int, QueryStatus>>
        {
            public string CommandName { get; set; } = null!;

            public ulong GuildId { get; set; }

            public ulong ChannelId { get; set; }

            public ulong UserId { get; set; }
        }

        public record Handler(ClemBotContext _context, IMediator _mediator)
            : IRequestHandler<Command, Result<int, QueryStatus>>
        {
            public async Task<Result<int, QueryStatus>> Handle(Command request, CancellationToken cancellationToken)
            {
                var invocationEntity = new CommandInvocation()
                {
                    CommandName = request.CommandName,
                    Time = DateTime.Now,
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
}
