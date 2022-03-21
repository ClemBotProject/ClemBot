using System.Linq;
using System.Threading;
using System.Threading.Tasks;
using ClemBot.Api.Common.Utilities;
using ClemBot.Api.Data.Contexts;
using ClemBot.Api.Services.Caching.CustomPrefix.Models;
using FluentValidation;
using MediatR;
using Microsoft.EntityFrameworkCore;

namespace ClemBot.Api.Core.Features.CustomPrefixes.Bot;

public class Delete
{
    public class Validator : AbstractValidator<Command>
    {
        public Validator()
        {
            RuleFor(p => p.GuildId).NotNull();
            RuleFor(p => p.Prefix).NotNull();
        }
    }

    public class Command : IRequest<IQueryResult<ulong>>
    {
        public ulong GuildId { get; set; }

        public string Prefix { get; set; } = null!;
    }

    public record Handler(ClemBotContext _context, IMediator _mediator) : IRequestHandler<Command, IQueryResult<ulong>>
    {
        public async Task<IQueryResult<ulong>> Handle(Command request, CancellationToken cancellationToken)
        {
            var guild = await _context.Guilds
                .Include(x => x.CustomPrefixes)
                .FirstOrDefaultAsync(g => g.Id == request.GuildId);

            if (guild is null)
            {
                return QueryResult<ulong>.NotFound();
            }

            if (guild.CustomPrefixes.All(x => x.Prefix != request.Prefix))
            {
                return QueryResult<ulong>.Success(request.GuildId);
            }

            var prefix = guild.CustomPrefixes.FirstOrDefault(x => x.Prefix == request.Prefix);

            guild.CustomPrefixes.Remove(prefix);
            await _context.SaveChangesAsync();

            // Clear the prefixes from the cache we fetch new values on the next message
            await _mediator.Send(new ClearCustomPrefixRequest { Id = request.GuildId });

            return QueryResult<ulong>.Success(request.GuildId);
        }
    }
}
