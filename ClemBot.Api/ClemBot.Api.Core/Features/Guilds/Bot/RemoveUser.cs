using System.Linq;
using System.Threading;
using System.Threading.Tasks;
using ClemBot.Api.Core.Utilities;
using ClemBot.Api.Data.Contexts;
using FluentValidation;
using MediatR;
using Microsoft.EntityFrameworkCore;

namespace ClemBot.Api.Core.Features.Guilds.Bot
{
    public class RemoveUser
    {
        public class Validator : AbstractValidator<Command>
        {
            public Validator()
            {
                RuleFor(p => p.GuildId).NotNull();
                RuleFor(p => p.UserId).NotNull();
            }
        }

        public class Command : IRequest<Result<ulong, QueryStatus>>
        {
            public ulong GuildId { get; set; }

            public ulong UserId { get; set; }
        }

        public record Handler(ClemBotContext _context) : IRequestHandler<Command, Result<ulong, QueryStatus>>
        {
            public async Task<Result<ulong, QueryStatus>> Handle(Command request, CancellationToken cancellationToken)
            {
                var guild = await _context.Guilds
                    .Include(y => y.Users)
                    .Where(x => x.Id == request.GuildId)
                    .FirstOrDefaultAsync();

                var user = await _context.Users
                    .Include(z => z.Roles)
                    .Where(x => x.Id == request.UserId)
                    .FirstOrDefaultAsync();

                if (!guild.Users.Contains(user))
                {
                    return QueryResult<ulong>.NotFound();
                }

                user.Roles.RemoveAll(x => x.GuildId == guild.Id);
                guild.Users.Remove(user);

                await _context.SaveChangesAsync();

                return QueryResult<ulong>.Success(guild.Id);
            }
        }
    }
}
