using System.Collections.Generic;
using System.Linq;
using System.Threading;
using System.Threading.Tasks;
using ClemBot.Api.Core.Security.Policies.GuildSandbox;
using ClemBot.Api.Core.Utilities;
using ClemBot.Api.Data.Contexts;
using ClemBot.Api.Data.Models;
using FluentValidation;
using MediatR;
using Microsoft.EntityFrameworkCore;

namespace ClemBot.Api.Core.Features.Guilds.Bot
{
    public class UpdateRoles
    {
        public class Validator : AbstractValidator<Command>
        {
            public Validator()
            {
                RuleFor(p => p.GuildId).NotNull();
                RuleFor(p => p.Roles).NotEmpty();
            }
        }

        public class RoleDto
        {
            public ulong Id { get; set; }

            public string? Name { get; set; }

            public bool Admin { get; set; }

            public List<ulong> Members { get; set; } = new();
        }

        public record Command : IRequest<Result<ulong, QueryStatus>>
        {
            public ulong GuildId { get; init; }

            public IReadOnlyList<RoleDto> Roles { get; set; } = new List<RoleDto>();
        }

        public record Handler(ClemBotContext _context)
            : IRequestHandler<Command, Result<ulong, QueryStatus>>
        {
            public async Task<Result<ulong, QueryStatus>> Handle(Command request, CancellationToken cancellationToken)
            {
                var guild = await _context.Guilds
                    .Where(x => x.Id == request.GuildId)
                    .Include(y => y.Roles)
                    .FirstOrDefaultAsync();


                if (guild is null)
                {
                    return QueryResult<ulong>.NotFound();
                }

                var roles = guild.Roles ?? new List<Role>();

                // Get all roles that are common to both enumerables and check for a name change
                foreach (var roleId in roles
                    .Select(x => x.Id)
                    .Intersect(request.Roles
                        .Select(x => x.Id)))
                {
                    var role = roles.First(x => x.Id == roleId);
                    role.Name = request.Roles.First(x => x.Id == roleId).Name;
                    role.Admin = request.Roles.First(x => x.Id == roleId).Admin;
                }

                // Get all roles that have been deleted
                foreach (var role in roles.Where(x => request.Roles.All(y => y.Id != x.Id)).ToList())
                {
                    _context.Roles.Remove(role);
                }

                // get new roles
                foreach (var role in request.Roles.Where(x => roles.All(y => y.Id != x.Id)))
                {
                    var roleEntity = new Role
                    {
                        Id = role.Id,
                        Name = role.Name,
                        GuildId = request.GuildId,
                        Admin = role.Admin,
                        IsAssignable = false
                    };

                    var members = await _context.Users
                        .Where(x => role.Members.Contains(x.Id))
                        .ToListAsync();

                    roleEntity.Users = members;

                    _context.Roles.Add(roleEntity);
                    guild.Roles?.Add(roleEntity);
                }

                // Reset Role Member mappings
                foreach (var roleDto in request.Roles)
                {
                    var role = await _context.Roles
                        .Include(y => y.Users)
                        .FirstOrDefaultAsync(x => roleDto.Id == x.Id);

                    var members = await _context.Users
                        .Where(x => roleDto.Members.Contains(x.Id))
                        .ToListAsync();

                    if (role is null)
                    {
                        continue;
                    }

                    role.Users.Clear();
                    role.Users = members;
                }

                await _context.SaveChangesAsync();

                return QueryResult<ulong>.Success(request.GuildId);
            }
        }
    }
}
