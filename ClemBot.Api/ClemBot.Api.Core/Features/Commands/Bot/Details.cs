using ClemBot.Api.Common;
using ClemBot.Api.Common.Extensions;
using ClemBot.Api.Data.Contexts;
using ClemBot.Api.Services.Caching.Channels.Models;
using ClemBot.Api.Services.Caching.Commands.Models;
using ClemBot.Api.Services.Caching.Guilds.Models;
using FluentValidation;

namespace ClemBot.Api.Core.Features.Commands.Bot;

public class Details
{
    public class Validator : AbstractValidator<Command>
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
        public string CommandName { get; set; } = null!;

        public bool Disabled { get; set; }

        public ulong GuildId { get; set; }

        public List<ulong> ChannelIds { get; set; } = new();
    }

    public class Command : IRequest<QueryResult<CommandRestrictionDto>>
    {
        public string CommandName { get; set; } = null!;

        public ulong GuildId { get; set; }

        public ulong ChannelId { get; set; }
    }

    public class Handler : IRequestHandler<Command, QueryResult<CommandRestrictionDto>>
    {
        private readonly IMediator _mediator;

        public Handler(IMediator mediator)
        {
            _mediator = mediator;
        }

        public async Task<QueryResult<CommandRestrictionDto>> Handle(Command request, CancellationToken cancellationToken)
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

            var channelIds = commandRestrictions
                .Select(cr => cr.ChannelId)
                .WhereNotNull()
                .ToList();

            return QueryResult<CommandRestrictionDto>.Success(new CommandRestrictionDto
            {
                CommandName = request.CommandName,
                Disabled = commandRestrictions.Count != 0,
                GuildId = request.GuildId,
                ChannelIds = channelIds
            });
        }
    }
}
