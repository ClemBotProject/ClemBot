using ClemBot.Api.Common.Security.Policies.GuildSandbox;
using ClemBot.Api.Common.Utilities;
using ClemBot.Api.Data.Contexts;
using ClemBot.Api.Data.Models;
using ClemBot.Api.Services.Caching.CustomTagPrefix.Models;
using FluentValidation;
using Microsoft.EntityFrameworkCore;

namespace ClemBot.Api.Core.Features.Tags;

public class SetCustomTagPrefix
{
    public class Validator : AbstractValidator<Command>
    {
        public Validator()
        {
            RuleFor(p => p.GuildId).NotNull();
            RuleFor(p => p.TagPrefix).NotNull();
        }
    }

    public class Command : IGuildSandboxModel, IRequest<IQueryResult<ulong>>
    {
        public ulong GuildId { get; init; }

        public string TagPrefix { get; set; } = null!;
    }

    public record Handler(ClemBotContext _context, IMediator _mediator) : IRequestHandler<Command, IQueryResult<ulong>>
    {
        public async Task<IQueryResult<ulong>> Handle(Command request, CancellationToken cancellationToken)
        {
            var guild = await _context.Guilds
                .Include(x => x.CustomTagPrefixes)
                .FirstOrDefaultAsync(g => g.Id == request.GuildId);

            if (guild is null)
            {
                return QueryResult<ulong>.NotFound();
            }

            var tagPrefix = new CustomTagPrefix
            {
                GuildId = request.GuildId,
                TagPrefix = request.TagPrefix
            };

            guild.CustomTagPrefixes.Clear();
            guild.CustomTagPrefixes.Add(tagPrefix);

            await _context.SaveChangesAsync();

            // Clear the prefixes from the cache we fetch new values on the next message
            await _mediator.Send(new ClearCustomTagPrefixRequest { Id = request.GuildId });

            return QueryResult<ulong>.Success(request.GuildId);
        }
    }
}
