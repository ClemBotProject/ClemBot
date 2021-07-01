using System.Collections.Generic;
using System.Globalization;
using System.IO;
using System.Linq;
using System.Threading;
using System.Threading.Tasks;
using ClemBot.Api.Core.Security.Policies.GuildSandbox;
using ClemBot.Api.Core.Utilities;
using ClemBot.Api.Data.Contexts;
using ClemBot.Api.Data.Models;
using CsvHelper;
using FluentValidation;
using MediatR;
using Microsoft.EntityFrameworkCore;

namespace ClemBot.Api.Core.Features.Guilds.Bot
{
    public class UpdateRolesUserMappings
    {
        public class RoleMappingDto
        {
            public ulong RoleId { get; set; }

            public ulong UserId { get; set; }
        }

        public record Command : IRequest<Result<ulong, QueryStatus>>
        {
            public ulong GuildId { get; init; }

            public string RoleMappingCsv { get; set; } = null!;
        }

        public record Handler(ClemBotContext _context)
            : IRequestHandler<Command, Result<ulong, QueryStatus>>
        {
            public async Task<Result<ulong, QueryStatus>> Handle(Command request, CancellationToken cancellationToken)
            {
                using var csvReader = new CsvReader(new StringReader(request.RoleMappingCsv), CultureInfo.InvariantCulture);
                var mappings = csvReader.GetRecords<RoleMappingDto>().ToList();

                var roles = _context.Roles
                    .Where(x =>
                        mappings.Select(y => y.RoleId).Contains(x.Id))
                    .Include(y => y.Users)
                    .ToList();

                var users = _context.Users
                    .Where(x =>
                        mappings.Select(y => y.UserId).Contains(x.Id))
                    .ToList();

                foreach (var role in mappings.GroupBy(x => x.RoleId).ToList())
                {
                    var mappedRole = roles.First(x => x.Id == role.Key);
                    var mappedUsers = users.Where(x => role.Select(z => z.UserId).Contains(x.Id));

                    mappedRole.Users.Clear();
                    mappedRole.Users.AddRange(mappedUsers);
                }

                await _context.SaveChangesAsync();

                return QueryResult<ulong>.Success(request.GuildId);
            }
        }
    }
}
