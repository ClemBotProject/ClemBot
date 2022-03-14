using ClemBot.Api.Common.Security.Policies.GuildSandbox;
using ClemBot.Api.Common.Utilities;
using ClemBot.Api.Data.Contexts;
using ClemBot.Api.Data.Models;
using ClemBot.Api.Services.Caching.CustomPrefix.Models;
using FluentValidation;
using Microsoft.EntityFrameworkCore;

namespace ClemBot.Api.Core.Features.CustomPrefixes;

public class Set
{
    public class Validator : AbstractValidator<Command>
    {
        public Validator()
        {
            RuleFor(p => p.GuildId).NotNull();
            RuleFor(p => p.Prefix).NotNull();
        }
    }

    public class Command : IGuildSandboxModel, IRequest<IQueryResult<ulong>>
    {
        public ulong GuildId { get; init; }

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

            var prefix = new CustomPrefix
            {
                GuildId = request.GuildId,
                Prefix = request.Prefix
            };

            guild.CustomPrefixes.Clear();
            guild.CustomPrefixes.Add(prefix);

            await _context.SaveChangesAsync();

            // Clear the prefixes from the cache we fetch new values on the next message
            await _mediator.Send(new ClearCustomPrefixRequest { Id = request.GuildId });

            return QueryResult<ulong>.Success(request.GuildId);
        }
    }
}
