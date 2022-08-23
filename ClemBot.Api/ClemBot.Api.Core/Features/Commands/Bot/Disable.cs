using ClemBot.Api.Data.Contexts;
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

    public class Query : IRequest<QueryResult<int>>
    {
        public string CommandName { get; set; } = null!;

        public ulong GuildId { get; set; }

        public ulong? ChannelId { get; set; }

        public bool SilentlyFail { get; set; }
    }

    public class Handler : IRequestHandler<Query, QueryResult<int>>
    {
        private readonly IMediator _mediator;
        private readonly ClemBotContext _context;

        public Handler(ClemBotContext context, IMediator mediator)
        {
            _context = context;
            _mediator = mediator;
        }

        public async Task<QueryResult<int>> Handle(Query request, CancellationToken cancellationToken)
        {
            var guildExists = await _mediator.Send(new GuildExistsRequest
            {
                Id = request.GuildId
            });

            var channelExists = false;
            if (request.ChannelId.HasValue)
            {
                channelExists = await _mediator.Send(new ChannelExistsRequest
                {
                    Id = request.ChannelId.Value
                });
            }

            if (!guildExists || request.ChannelId.HasValue && !channelExists)
            {
                return QueryResult<int>.NotFound();
            }

            var commandRestrictions = await _mediator.Send(new GetCommandRestrictionRequest
            {
                CommandName = request.CommandName, Id = request.GuildId
            });


        }
    }
}
