using System.Collections.Generic;
using System.Globalization;
using System.IO;
using System.Linq;
using System.Threading;
using System.Threading.Tasks;
using ClemBot.Api.Common.Utilities;
using ClemBot.Api.Core.Features.Authorization;
using ClemBot.Api.Data.Contexts;
using ClemBot.Api.Data.Models;
using CsvHelper;
using FluentValidation;
using MediatR;
using Microsoft.EntityFrameworkCore;

namespace ClemBot.Api.Core.Features.Guilds.Bot;

public class UpdateRoles
{
    public class RoleDto
    {
        public ulong Id { get; set; }

        public string? Name { get; set; }

        public bool Admin { get; set; }
    }

    public record Command : IRequest<IQueryResult<ulong>>
    {
        public ulong GuildId { get; init; }

        public string RoleCsv { get; set; } = null!;
    }

    public record Handler(ClemBotContext _context, ILogger<Handler> _logger)
        : IRequestHandler<Command, IQueryResult<ulong>>
    {
        public async Task<IQueryResult<ulong>> Handle(Command request, CancellationToken cancellationToken)
        {
            _logger.LogInformation("Beginning UpdateRoles CSV Deserialization");

            using var csvReader = new CsvReader(new StringReader(request.RoleCsv), CultureInfo.InvariantCulture);
            var roles = csvReader.GetRecords<RoleDto>().ToList();

            var guildEntity = await _context.Guilds
                .Include(y => y.Roles)
                .FirstOrDefaultAsync(x => x.Id == request.GuildId);

            if (guildEntity is null)
            {
                return QueryResult<ulong>.NotFound();
            }

            var rolesEntity = guildEntity.Roles ?? new List<Role>();

            // Get all roles that are common to both enumerables and check for a name change
            foreach (var roleId in rolesEntity
                         .Select(x => x.Id)
                         .Intersect(roles
                             .Select(x => x.Id)))
            {
                var role = rolesEntity.First(x => x.Id == roleId);
                role.Name = roles.First(x => x.Id == roleId).Name;
                role.Admin = roles.First(x => x.Id == roleId).Admin;
            }

            // Get all roles that have been deleted
            foreach (var role in rolesEntity.Where(x => roles.All(y => y.Id != x.Id)).ToList())
            {
                _context.Roles.Remove(role);
            }

            // get new roles
            foreach (var role in roles.Where(x => rolesEntity.All(y => y.Id != x.Id)))
            {
                var roleEntity = new Role
                {
                    Id = role.Id,
                    Name = role.Name,
                    GuildId = request.GuildId,
                    Admin = role.Admin,
                    IsAssignable = false
                };

                _context.Roles.Add(roleEntity);
                guildEntity.Roles?.Add(roleEntity);
            }

            await _context.SaveChangesAsync();

            return QueryResult<ulong>.Success(request.GuildId);
        }
    }
}
