using System.Linq;
using System.Threading;
using System.Threading.Tasks;
using ClemBot.Api.Common.Utilities;
using ClemBot.Api.Data.Contexts;
using FluentValidation;
using MediatR;
using Microsoft.EntityFrameworkCore;

namespace ClemBot.Api.Core.Features.Guilds.Bot;

public class AddUser
{
    public class Validator : AbstractValidator<Command>
    {
        public Validator()
        {
            RuleFor(p => p.GuildId).NotNull();
            RuleFor(p => p.UserId).NotNull();
        }
    }

    public class Command : IRequest<IQueryResult<ulong>>
    {
        public ulong GuildId { get; set; }

        public ulong UserId { get; set; }
    }

    public record Handler(ClemBotContext _context) : IRequestHandler<Command, IQueryResult<ulong>>
    {
        public async Task<IQueryResult<ulong>> Handle(Command request, CancellationToken cancellationToken)
        {
            var guild = await _context.Guilds
                .Where(x => x.Id == request.GuildId)
                .Include(y => y.Users)
                .FirstOrDefaultAsync();

            if (guild is null)
            {
                return QueryResult<ulong>.NotFound();
            }

            var user = await _context.Users
                .Where(x => x.Id == request.UserId)
                .Include(y => y.Guilds)
                .FirstOrDefaultAsync();

            if (guild.Users.Contains(user))
            {
                return QueryResult<ulong>.Conflict();
            }

            guild.Users.Add(user);
            await _context.SaveChangesAsync();

            return QueryResult<ulong>.Success(guild.Id);
        }
    }
}
