using System.Collections.Generic;
using System.Linq;
using System.Threading;
using System.Threading.Tasks;
using ClemBot.Api.Common.Utilities;
using ClemBot.Api.Data.Contexts;
using ClemBot.Api.Data.Models;
using FluentValidation;
using MediatR;
using Microsoft.EntityFrameworkCore;
using NuGet.Packaging;

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

    public record Command : IRequest<QueryResult<IEnumerable<ulong>>>
    {
        public ulong Id { get; set; }

        public List<ulong> Roles { get; set; } = new();
    }

    public record Handler(ClemBotContext _context) : IRequestHandler<Command, QueryResult<IEnumerable<ulong>>>
    {
        public async Task<QueryResult<IEnumerable<ulong>>> Handle(Command request, CancellationToken cancellationToken)
        {
            var roleMappings = await _context.RoleUser
                .Select(ru => new { ru, ru.Role.GuildId })
                .Where(ru => ru.ru.UserId == request.Id)
                .ToListAsync();

            if (!roleMappings.Any())
            {
                return QueryResult<IEnumerable<ulong>>.NotFound();
            }

            var guildId = roleMappings.First(ru => request.Roles.Contains(ru.ru.RoleId)).GuildId;

            var oldRoleMappings = roleMappings
                .Where(ru => ru.GuildId == guildId && !request.Roles.Contains(ru.ru.RoleId))
                .Select(ru => ru.ru);

            var newRoleMappings = request.Roles
                .Where(r => roleMappings.All(ru => ru.ru.RoleId != r))
                .Select(r => new RoleUser() {RoleId = r, UserId = request.Id});

            _context.RoleUser.RemoveRange(oldRoleMappings);
            _context.RoleUser.AddRange(newRoleMappings);

            await _context.SaveChangesAsync();

            return QueryResult<IEnumerable<ulong>>.Success(request.Roles);
        }
    }
}
