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
        public class RoleDto
        {
            public ulong Id { get; set; }

            public string? Name { get; set; }

            public bool Admin { get; set; }

            public List<ulong> Members { get; set; } = new();
        }

        public record GuildDto
        {
            public ulong GuildId { get; init; }

            public IReadOnlyList<RoleDto> Roles { get; set; } = new List<RoleDto>();
        }

        public record Command : IRequest<Result<IEnumerable<ulong>, QueryStatus>>
        {
            public IReadOnlyList<GuildDto> Guilds { get; set; } = new List<GuildDto>();
        }

        public record Handler(ClemBotContext _context)
            : IRequestHandler<Command, Result<IEnumerable<ulong>, QueryStatus>>
        {
            public async Task<Result<IEnumerable<ulong>, QueryStatus>> Handle(Command request, CancellationToken cancellationToken)
            {
                var guilds = await _context.Guilds
                    .Include(y => y.Roles)
                    .ToListAsync();

                foreach (var requestGuild in request.Guilds)
                {
                    var guildEntity = guilds.FirstOrDefault(x => x.Id == requestGuild.GuildId);

                    if (guildEntity is null)
                    {
                        continue;
                    }
                    var roles = guildEntity.Roles ?? new List<Role>();

                    // Get all roles that are common to both enumerables and check for a name change
                    foreach (var roleId in roles
                        .Select(x => x.Id)
                        .Intersect(requestGuild.Roles
                            .Select(x => x.Id)))
                    {
                        var role = roles.First(x => x.Id == roleId);
                        role.Name = requestGuild.Roles.First(x => x.Id == roleId).Name;
                        role.Admin = requestGuild.Roles.First(x => x.Id == roleId).Admin;
                    }

                    // Get all roles that have been deleted
                    foreach (var role in roles.Where(x => requestGuild.Roles.All(y => y.Id != x.Id)).ToList())
                    {
                        _context.Roles.Remove(role);
                    }

                    // get new roles
                    foreach (var role in requestGuild.Roles.Where(x => roles.All(y => y.Id != x.Id)))
                    {
                        var roleEntity = new Role
                        {
                            Id = role.Id,
                            Name = role.Name,
                            GuildId = requestGuild.GuildId,
                            Admin = role.Admin,
                            IsAssignable = false
                        };

                        var members = await _context.Users
                            .Where(x => role.Members.Contains(x.Id))
                            .ToListAsync();

                        roleEntity.Users = members;

                        _context.Roles.Add(roleEntity);
                        guildEntity.Roles?.Add(roleEntity);
                    }

                    // Reset Role Member mappings
                    foreach (var roleDto in requestGuild.Roles)
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
                }

                await _context.SaveChangesAsync();

                return QueryResult<IEnumerable<ulong>>.Success(request.Guilds.Select(x => x.GuildId));
            }
        }
    }
}
