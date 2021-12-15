using System.Linq;
using System.Threading;
using System.Threading.Tasks;
using ClemBot.Api.Common.Utilities;
using ClemBot.Api.Data.Contexts;
using ClemBot.Api.Data.Models;
using FluentValidation;
using MediatR;
using Microsoft.EntityFrameworkCore;

namespace ClemBot.Api.Core.Features.DesignatedChannels.Bot;

public class Register
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

    public record Handler(ClemBotContext _context) : IRequestHandler<Command, IQueryResult<ulong>>
    {
        public async Task<IQueryResult<ulong>> Handle(Command request, CancellationToken cancellationToken)
        {
            var mapping = new DesignatedChannelMapping()
            {
                ChannelId = request.ChannelId,
                Type = request.Designation
            };

            var channel = await _context.Channels
                .FirstOrDefaultAsync(x => x.Id == request.ChannelId && !x.IsThread);

            if (channel is null)
            {
                return QueryResult<ulong>.Invalid(request.ChannelId);
            }

            var dcMappings = await _context.DesignatedChannelMappings.FirstOrDefaultAsync(x =>
                x.ChannelId == request.ChannelId && x.Type == request.Designation);

            if (dcMappings is not null)
            {
                return QueryResult<ulong>.Conflict();
            }

            _context.DesignatedChannelMappings.Add(mapping);
            await _context.SaveChangesAsync();

            return QueryResult<ulong>.Success(request.ChannelId);
        }
    }
}
