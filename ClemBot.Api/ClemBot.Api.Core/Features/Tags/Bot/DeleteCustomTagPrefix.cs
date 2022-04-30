using System.Linq;
using System.Threading;
using System.Threading.Tasks;
using ClemBot.Api.Common.Utilities;
using ClemBot.Api.Data.Contexts;
using ClemBot.Api.Services.Caching.CustomTagPrefix.Models;
using FluentValidation;
using MediatR;
using Microsoft.EntityFrameworkCore;

namespace ClemBot.Api.Core.Features.Tags.Bot;

public class DeleteCustomTagPrefix
{
    public class Validator : AbstractValidator<Command>
    {
        public Validator()
        {
            RuleFor(p => p.GuildId).NotNull();
            RuleFor(p => p.TagPrefix).NotNull();
        }
    }

    public class Command : IRequest<IQueryResult<ulong>>
    {
        public ulong GuildId { get; set; }

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

            if (guild.CustomTagPrefixes.All(x => x.TagPrefix != request.TagPrefix))
            {
                return QueryResult<ulong>.Success(request.GuildId);
            }

            var tagPrefix = guild.CustomTagPrefixes.FirstOrDefault(x => x.TagPrefix == request.TagPrefix);

            guild.CustomTagPrefixes.Remove(tagPrefix);
            await _context.SaveChangesAsync();

            // Clear the inline prefixes from the cache we fetch new values on the next message
            await _mediator.Send(new ClearCustomTagPrefixRequest { Id = request.GuildId });

            return QueryResult<ulong>.Success(request.GuildId);
        }
    }
}
