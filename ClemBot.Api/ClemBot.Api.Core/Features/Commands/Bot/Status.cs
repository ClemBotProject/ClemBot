using ClemBot.Api.Common;
using ClemBot.Api.Data.Contexts;
using ClemBot.Api.Services.Caching.Channels.Models;
using ClemBot.Api.Services.Caching.Commands.Models;
using ClemBot.Api.Services.Caching.Guilds.Models;
using FluentValidation;

namespace ClemBot.Api.Core.Features.Commands.Bot;

public class Status
{
    public class Validator : AbstractValidator<Query>
    {
        public Validator()
        {
            RuleFor(c => c.CommandName).NotNull().NotEmpty();
            RuleFor(c => c.GuildId).NotNull();
            RuleFor(c => c.ChannelId).NotNull();
        }
    }

    public class CommandRestrictionDto : IResponseModel
    {
        public bool Disabled { get; set; }

        public bool? SilentlyFail { get; set; }
    }

    public class Query : IRequest<QueryResult<CommandRestrictionDto>>
    {
        public string CommandName { get; set; } = null!;

        public ulong GuildId { get; set; }

        public ulong ChannelId { get; set; }
    }

    public class Handler : IRequestHandler<Query, QueryResult<CommandRestrictionDto>>
    {
        private readonly IMediator _mediator;

        public Handler(IMediator mediator)
        {
            _mediator = mediator;
        }

        public async Task<QueryResult<CommandRestrictionDto>> Handle(Query request, CancellationToken cancellationToken)
        {
            var guildExists = await _mediator.Send(new GuildExistsRequest
            {
                Id = request.GuildId
            });

            var channelExists = await _mediator.Send(new ChannelExistsRequest
            {
                Id = request.ChannelId
            });

            if (!guildExists || !channelExists)
            {
                return QueryResult<CommandRestrictionDto>.NotFound();
            }

            var commandRestrictions = await _mediator.Send(new GetCommandRestrictionRequest
            {
                CommandName = request.CommandName,
                Id = request.GuildId
            });

            // Check if we have a white listed command restriction, always allow that
            if (commandRestrictions.Any(x => x.ChannelId is not null &&
                                             x.ChannelId == request.ChannelId &&
                                             x.RestrictionType == CommandRestrictionType.WhiteList))
            {
                return QueryResult<CommandRestrictionDto>.Success(new CommandRestrictionDto
                {
                    Disabled = false,
                    SilentlyFail = null
                });
            }

            var disabled = false;
            bool? silentlyFail = false;

            foreach (var restriction in commandRestrictions)
            {
                // check for server-wide ban or if the command is banned in the requested channel
                if (restriction.ChannelId is null || restriction.ChannelId == request.ChannelId)
                {
                    disabled = true;
                    silentlyFail = restriction.SilentlyFail;
                    break;
                }
            }

            return QueryResult<CommandRestrictionDto>.Success(new CommandRestrictionDto
            {
                Disabled = disabled,
                SilentlyFail = silentlyFail
            });
        }
    }
}
