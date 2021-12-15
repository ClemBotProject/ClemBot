using System.Collections.Generic;
using System.Linq;
using System.Threading;
using System.Threading.Tasks;
using ClemBot.Api.Common.Utilities;
using ClemBot.Api.Data.Contexts;
using FluentValidation;
using MediatR;
using Microsoft.EntityFrameworkCore;

namespace ClemBot.Api.Core.Features.Users.Bot;

public class UpdateRoles
{
    public class Validator : AbstractValidator<Command>
    {
        public Validator()
        {
            RuleFor(p => p.Id).NotNull();
        }
    }

    public record Command : IRequest<IQueryResult<IEnumerable<ulong>>>
    {
        public ulong Id { get; set; }

        public List<ulong> Roles { get; set; } = new();
    }

    public record Handler(ClemBotContext _context) : IRequestHandler<Command, IQueryResult<IEnumerable<ulong>>>
    {
        public async Task<IQueryResult<IEnumerable<ulong>>> Handle(Command request, CancellationToken cancellationToken)
        {
            var roles = await _context.Roles
                .Where(x => request.Roles.Contains(x.Id))
                .ToListAsync();

            var user = await _context.Users
                .Include(y => y.Roles)
                .FirstOrDefaultAsync(x => x.Id == request.Id);

            if (roles is null || !roles.Any() || user is null)
            {
                return QueryResult<IEnumerable<ulong>>.NotFound();
            }

            user.Roles.RemoveAll(x => x.GuildId == roles.First().GuildId);
            user.Roles.AddRange(roles);
            await _context.SaveChangesAsync();

            return QueryResult<IEnumerable<ulong>>.Success(roles.Select(x => x.Id));
        }
    }
}
