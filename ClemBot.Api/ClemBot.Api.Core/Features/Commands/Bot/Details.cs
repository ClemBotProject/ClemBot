using ClemBot.Api.Common;
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
            RuleFor(c => c.CommandName).NotNull();
            RuleFor(c => c.GuildId).NotNull();
            RuleFor(c => c.ChannelId).NotNull();
        }
    }

    public class CommandRestrictionDto : IResponseModel
    {
        public string CommandName { get; init; } = null!;

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
        private readonly ClemBotContext _context;

        public Handler(ClemBotContext context, IMediator mediator)
        {
            _context = context;
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

            var list = await _mediator.Send(new GetCommandRestrictionRequest
            {
                CommandName = request.CommandName,
                Id = request.GuildId
            });

            var channelIds = new List<ulong>();
            foreach (var restriction in list)
            {
                if (restriction.Channel != null)
                {
                    channelIds.Add(restriction.ChannelId);
                }
            }

            return QueryResult<CommandRestrictionDto>.Success(new CommandRestrictionDto
            {
                CommandName = request.CommandName,
                Disabled = list.Count != 0,
                GuildId = request.GuildId,
                ChannelIds = channelIds
            });
        }
    }
}
