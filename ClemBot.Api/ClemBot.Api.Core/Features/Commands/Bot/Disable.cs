using ClemBot.Api.Data.Contexts;
using ClemBot.Api.Data.Models;
using ClemBot.Api.Services.Caching.Channels.Models;
using ClemBot.Api.Services.Caching.Commands.Models;
using ClemBot.Api.Services.Caching.Guilds.Models;
using FluentValidation;

namespace ClemBot.Api.Core.Features.Commands.Bot;

public class Disable
{

    public class Validator : AbstractValidator<Query>
    {
        public Validator()
        {
            RuleFor(c => c.CommandName).NotNull().NotEmpty();
            RuleFor(c => c.GuildId).NotNull();
            RuleFor(c => c.SilentlyFail).NotNull();
        }
    }

    public class Query : IRequest<QueryResult<Unit>>
    {
        public string CommandName { get; set; } = null!;

        public ulong GuildId { get; set; }

        public ulong? ChannelId { get; set; }

        public bool SilentlyFail { get; set; }
    }

    public class Handler : IRequestHandler<Query, QueryResult<Unit>>
    {
        private readonly IMediator _mediator;
        private readonly ClemBotContext _context;

        public Handler(ClemBotContext context, IMediator mediator)
        {
            _context = context;
            _mediator = mediator;
        }

        public async Task<QueryResult<Unit>> Handle(Query request, CancellationToken cancellationToken)
        {
            var guildExists = await _mediator.Send(new GuildExistsRequest
            {
                Id = request.GuildId
            });

            var channelExists = false;
            if (request.ChannelId is not null)
            {
                channelExists = await _mediator.Send(new ChannelExistsRequest
                {
                    Id = request.ChannelId.Value
                });
            }

            if (!guildExists || (request.ChannelId is not null && !channelExists))
            {
                return QueryResult<Unit>.NotFound();
            }

            var commandRestrictions = await _mediator.Send(new GetCommandRestrictionRequest
            {
                CommandName = request.CommandName,
                Id = request.GuildId
            });

            if (request.ChannelId is not null)
            {
                // check for an already-disabled command, server-wide or requested channel
                if (commandRestrictions.Any(r => r.ChannelId is null || r.ChannelId == request.ChannelId.Value))
                {
                    return QueryResult<Unit>.Conflict();
                }

                _context.CommandRestrictions.Add(new CommandRestriction
                {
                    CommandName = request.CommandName,
                    GuildId = request.GuildId,
                    ChannelId = request.ChannelId.Value,
                    SilentlyFail = request.SilentlyFail
                });
                await _context.SaveChangesAsync();
                await _mediator.Send(new ClearCommandRestrictionRequest
                {
                    CommandName = request.CommandName,
                    Id = request.GuildId
                });
                return QueryResult<Unit>.NoContent();
            }

            // remove previous channel-bound restrictions
            foreach (var restriction in commandRestrictions)
            {
                if (restriction.ChannelId is null)
                {
                    return QueryResult<Unit>.Conflict();
                }
                _context.CommandRestrictions.Remove(restriction);
            }

            _context.Add(new CommandRestriction
            {
                CommandName = request.CommandName,
                GuildId = request.GuildId,
                SilentlyFail = request.SilentlyFail
            });
            await _context.SaveChangesAsync();
            await _mediator.Send(new ClearCommandRestrictionRequest
            {
                CommandName = request.CommandName,
                Id = request.GuildId
            });
            return QueryResult<Unit>.NoContent();
        }
    }
}
