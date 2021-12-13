using System.Threading;
using System.Threading.Tasks;
using ClemBot.Api.Common.Utilities;
using ClemBot.Api.Data.Contexts;
using ClemBot.Api.Data.Models;
using FluentValidation;
using MediatR;
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

    public class Command : IRequest<IQueryResult<ulong>>
    {
        public ulong ChannelId { get; set; }

        public Common.Enums.DesignatedChannels Designation { get; set; }
    }

    public record QueryHandler(ClemBotContext _context) : IRequestHandler<Command, IQueryResult<ulong>>
    {
        public async Task<IQueryResult<ulong>> Handle(Command request, CancellationToken cancellationToken)
        {

            var dcMappings = await _context.DesignatedChannelMappings
                .FirstOrDefaultAsync(x => x.ChannelId == request.ChannelId && x.Type == request.Designation);

            if (dcMappings is null)
            {
                return QueryResult<ulong>.NotFound();
            }

            _context.DesignatedChannelMappings.Remove(dcMappings);
            await _context.SaveChangesAsync();

            return QueryResult<ulong>.Success(request.ChannelId);
        }
    }
}
