using ClemBot.Api.Common;
using ClemBot.Api.Common.Extensions;
using ClemBot.Api.Data.Contexts;
using ClemBot.Api.Data.Models;
using ClemBot.Api.Services.Caching.Channels.Models;
using ClemBot.Api.Services.Caching.Commands.Models;
using ClemBot.Api.Services.Caching.Guilds.Models;
using FluentValidation;

namespace ClemBot.Api.Core.Features.Commands.Bot;

public class Details
{
    public record BlackListedChannelDto(ulong? ChannelId, bool? SilentlyFail);

    public class Validator : AbstractValidator<Command>
    {
        public Validator()
        {
            RuleFor(c => c.CommandName).NotNull().NotEmpty();
            RuleFor(c => c.GuildId).NotNull();
        }
    }

    public class CommandRestrictionDto : IResponseModel
    {
        public string CommandName { get; set; } = null!;

        public ulong GuildId { get; set; }

        public bool GuildDisabled { get; set; }

        public List<BlackListedChannelDto> BlackListedChannelIds { get; set; } = new();

        public List<ulong> WhiteListedChannelIds { get; set; } = new();
    }

    public class Command : IRequest<QueryResult<CommandRestrictionDto>>
    {
        public string CommandName { get; set; } = null!;

        public ulong GuildId { get; set; }
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

            if (!guildExists)
            {
                return QueryResult<CommandRestrictionDto>.NotFound();
            }

            var commandRestrictions = await _mediator.Send(new GetCommandRestrictionRequest
            {
                CommandName = request.CommandName,
                Id = request.GuildId
            });

            var blacklistChannelIds = commandRestrictions
                .Where(x => x.ChannelId is not null && x.RestrictionType == CommandRestrictionType.BlackList)
                .Select(x => new BlackListedChannelDto(x.ChannelId, x.SilentlyFail))
                .ToList();

            var whitelistChannelIds = commandRestrictions
                .Where(x => x.ChannelId is not null && x.RestrictionType == CommandRestrictionType.WhiteList)
                .Select(x => x.ChannelId)
                .WhereNotNull()
                .ToList();

            return QueryResult<CommandRestrictionDto>.Success(new CommandRestrictionDto
            {
                CommandName = request.CommandName,
                GuildDisabled = commandRestrictions.Any(x => x.ChannelId is null),
                GuildId = request.GuildId,
                BlackListedChannelIds = blacklistChannelIds,
                WhiteListedChannelIds = whitelistChannelIds
            });
        }
    }
}
