using System.Linq;
using System.Threading;
using System.Threading.Tasks;
using ClemBot.Api.Core.Utilities;
using ClemBot.Api.Data.Contexts;
using FluentValidation;
using MediatR;
using Microsoft.EntityFrameworkCore;

namespace ClemBot.Api.Core.Features.CustomPrefixes.Bot
{
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

        public class Command : IRequest<Result<ulong, QueryStatus>>
        {
            public ulong GuildId { get; set; }

            public string Prefix { get; set; } = null!;
        }

        public record Handler(ClemBotContext _context) : IRequestHandler<Command, Result<ulong, QueryStatus>>
        {
            public async Task<Result<ulong, QueryStatus>> Handle(Command request, CancellationToken cancellationToken)
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

                return QueryResult<ulong>.Success(request.GuildId);
            }
        }
    }
}
