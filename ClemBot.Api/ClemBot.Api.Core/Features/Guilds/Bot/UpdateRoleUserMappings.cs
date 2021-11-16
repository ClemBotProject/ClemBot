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
using LinqToDB;
using LinqToDB.Data;
using LinqToDB.EntityFrameworkCore;
using MediatR;
using Microsoft.EntityFrameworkCore;

namespace ClemBot.Api.Core.Features.Guilds.Bot;

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

            var roleSet = mappings
                .Select(y => y.RoleId)
                .ToHashSet();

            // Its faster to just clear all the role mappings and bulk insert again then it is to
            // query which ones we need

            await _context.RoleUser
                .Where(x => roleSet.Contains(x.RoleId))
                .DeleteAsync();

            var mappedEntities = mappings.Select(x => new RoleUser() { RoleId = x.RoleId, UserId = x.UserId });

            await _context.BulkCopyAsync(new BulkCopyOptions()
            {
                BulkCopyType = BulkCopyType.ProviderSpecific,
            }, mappedEntities);

            return QueryResult<ulong>.Success(request.GuildId);
        }
    }
}