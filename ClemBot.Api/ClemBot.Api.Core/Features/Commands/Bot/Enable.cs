using ClemBot.Api.Data.Contexts;
using ClemBot.Api.Data.Models;
using ClemBot.Api.Services.Caching.Channels.Models;
using ClemBot.Api.Services.Caching.Commands.Models;
using ClemBot.Api.Services.Caching.Guilds.Models;
using FluentValidation;

namespace ClemBot.Api.Core.Features.Commands.Bot;

public class Enable
{

    public class Validator : AbstractValidator<Query>
    {
        public Validator()
        {
            RuleFor(c => c.CommandName).NotNull().NotEmpty();
            RuleFor(c => c.GuildId).NotNull();
        }
    }

    public class Query : IRequest<QueryResult<Unit>>
    {
        public string CommandName { get; set; } = null!;

        public ulong GuildId { get; set; }

        public ulong? ChannelId { get; set; }
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

            // can't enable what isn't disabled
            if (commandRestrictions.Count == 0)
            {
                return QueryResult<Unit>.NotFound();
            }

            if (request.ChannelId is not null)
            {
                // Check if we have global restriction so that we know to
                // Whitelist the command instead of removing a blacklist
                var guildRestriction = commandRestrictions
                    .FirstOrDefault(r => r.ChannelId is null);

                if (guildRestriction is not null)
                {
                    // Check if we already have a white list for this channel
                    if (commandRestrictions.Any(x => x.ChannelId == request.ChannelId &&
                                                      x.RestrictionType == CommandRestrictionType.WhiteList))
                    {
                        return QueryResult<Unit>.Conflict();
                    }

                    var entity = new CommandRestriction
                    {
                        CommandName = request.CommandName,
                        GuildId = request.GuildId,
                        RestrictionType = CommandRestrictionType.WhiteList,
                        ChannelId = request.ChannelId,
                        SilentlyFail = null
                    };

                    _context.CommandRestrictions.Add(entity);
                    await _context.SaveChangesAsync();

                    await _mediator.Send(new ClearCommandRestrictionRequest
                    {
                        CommandName = request.CommandName,
                        Id = request.GuildId
                    });

                    return QueryResult<Unit>.NoContent();
                }

                // Check if we have a single channel black list
                var cr = commandRestrictions
                    .FirstOrDefault(r => r.ChannelId is not null && r.ChannelId == request.ChannelId);

                if (cr is null)
                {
                    return QueryResult<Unit>.NotFound();
                }

                _context.CommandRestrictions.Remove(cr);
                await _context.SaveChangesAsync();

                await _mediator.Send(new ClearCommandRestrictionRequest
                {
                    CommandName = request.CommandName,
                    Id = request.GuildId
                });
                return QueryResult<Unit>.NoContent();
            }

            // Remove all restrictions on this command
            _context.CommandRestrictions.RemoveRange(commandRestrictions);
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
