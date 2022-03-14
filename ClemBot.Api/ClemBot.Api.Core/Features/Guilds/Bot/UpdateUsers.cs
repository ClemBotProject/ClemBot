using System.Collections.Generic;
using System.Collections.Immutable;
using System.Globalization;
using System.IO;
using System.Linq;
using System.Threading;
using System.Threading.Tasks;
using ClemBot.Api.Common.Utilities;
using ClemBot.Api.Data.Contexts;
using ClemBot.Api.Data.Models;
using CsvHelper;
using LinqToDB;
using LinqToDB.Data;
using LinqToDB.EntityFrameworkCore;
using LinqToDB.Tools;
using MediatR;
using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.Logging;

namespace ClemBot.Api.Core.Features.Guilds.Bot;

public class UpdateUsers
{
    public record UserDto
    {
        public ulong UserId { get; set; }

        public string? Name { get; set; }
    }

    public record Command : IRequest<IQueryResult<ulong>>
    {
        public ulong GuildId { get; init; }

        public string UserCsv { get; set; } = null!;
    }

    public record Handler(ClemBotContext _context, ILogger<UpdateUsers> _logger)
        : IRequestHandler<Command, IQueryResult<ulong>>
    {
        public async Task<IQueryResult<ulong>> Handle(Command request, CancellationToken cancellationToken)
        {
            _logger.LogInformation("Beginning UpdateUsers CSV Deserialization");

            using var csvReader = new CsvReader(new StringReader(request.UserCsv), CultureInfo.InvariantCulture);
            var users = csvReader.GetRecords<UserDto>().ToList();

            _logger.LogInformation("UpdateUsers CSV Deserialization succeeded");

            var usersDb = (await _context.Users
                    .Select(x => x.Id)
                    .ToListAsyncEF())
                .ToImmutableHashSet();

            var guildEntity = await _context.Guilds
                .Include(y => y.Users)
                .FirstOrDefaultAsyncEF(x => x.Id == request.GuildId);

            if (guildEntity is null)
            {
                return QueryResult<ulong>.NotFound();
            }

            var newUsers = new List<User>();
            var newGuildUsers = new List<GuildUser>();

            var guildUsersSet = guildEntity.Users.Select(x => x.Id).ToHashSet();

            foreach (var user in users)
            {
                _logger.LogTrace("Updating {User}", user);

                if (!usersDb.Contains(user.UserId))
                {
                    _logger.LogTrace("Adding new {User}", user);
                    var userEntity = new User { Id = user.UserId, Name = user.Name };

                    newUsers.Add(userEntity);
                    newGuildUsers.Add(new GuildUser { GuildId = request.GuildId, UserId = user.UserId });
                }
                else if (!guildUsersSet.Contains(user.UserId))
                {
                    _logger.LogTrace("Adding new user guild mapping {User}", user);
                    newGuildUsers.Add(new GuildUser { GuildId = request.GuildId, UserId = user.UserId });
                }
            }

            _logger.LogInformation("Saving UpdateUser Changes");

            /*
             * We need to bulk copy here so that we can handle high load guilds
             * without this our api will crash attempting to add all the users
             */

            if (newUsers.Count > 0)
            {
                await _context.BulkCopyAsync(new BulkCopyOptions
                {
                    BulkCopyType = BulkCopyType.ProviderSpecific
                }, newUsers);
            }

            if (newGuildUsers.Count > 0)
            {
                await _context.BulkCopyAsync(new BulkCopyOptions
                {
                    BulkCopyType = BulkCopyType.ProviderSpecific
                }, newGuildUsers);
            }

            await _context.GuildUser
                .Where(x => x.GuildId == request.GuildId && !users.Select(y => y.UserId)
                    .Contains(x.UserId))
                .DeleteAsync();

            return QueryResult<ulong>.Success(request.GuildId);
        }
    }
}
