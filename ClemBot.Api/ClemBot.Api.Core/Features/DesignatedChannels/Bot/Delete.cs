using ClemBot.Api.Data.Contexts;
using ClemBot.Api.Services.Caching.DesignatedChannels.Models;
using FluentValidation;
using Microsoft.EntityFrameworkCore;

namespace ClemBot.Api.Core.Features.DesignatedChannels.Bot;

public class Delete
{
    public class Validator : AbstractValidator<Command>
    {
        public Validator()
        {
            RuleFor(x => x.ChannelId).NotNull();
            RuleFor(x => x.Designation).NotNull();
        }
    }

    public class Command : IRequest<QueryResult<ulong>>
    {
        public ulong ChannelId { get; set; }

        public Common.Enums.DesignatedChannels Designation { get; set; }
    }

    public class QueryHandler : IRequestHandler<Command, QueryResult<ulong>>
    {
        private ClemBotContext _context { get; init; }

        private IMediator _mediator { get; init; }

        public QueryHandler(ClemBotContext context, IMediator mediator)
        {
            _context = context;
            _mediator = mediator;
        }

        public async Task<QueryResult<ulong>> Handle(Command request, CancellationToken cancellationToken)
        {

            var dcMappings = await _context.DesignatedChannelMappings
                .FirstOrDefaultAsync(x => x.ChannelId == request.ChannelId && x.Type == request.Designation);

            if (dcMappings is null)
            {
                return QueryResult<ulong>.NotFound();
            }

            _context.DesignatedChannelMappings.Remove(dcMappings);
            await _context.SaveChangesAsync();

            var guildId = await _context.Channels
                .Where(x => x.Id == request.ChannelId)
                .Select(x => x.GuildId)
                .FirstAsync();

            // Clear the cached entry
            await _mediator.Send(
                new ClearDesignatedChannelDetailRequest { Id = guildId, Designation = request.Designation });

            return QueryResult<ulong>.Success(request.ChannelId);
        }
    }
}
