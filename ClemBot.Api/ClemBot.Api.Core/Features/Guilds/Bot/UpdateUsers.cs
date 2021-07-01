using System.Collections.Generic;
using System.Globalization;
using System.IO;
using System.Linq;
using System.Threading;
using System.Threading.Tasks;
using ClemBot.Api.Core.Utilities;
using ClemBot.Api.Data.Contexts;
using ClemBot.Api.Data.Models;
using CsvHelper;
using MediatR;
using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.Logging;

namespace ClemBot.Api.Core.Features.Guilds.Bot
{
    public class UpdateUsers
    {
        public record UserDto
        {
            public ulong UserId { get; set; }

            public string? Name { get; set; }
        }

        public record Command : IRequest<Result<ulong, QueryStatus>>
        {
            public ulong GuildId { get; init; }

            public string UserCsv { get; set; } = null!;
        }

        public record Handler(ClemBotContext _context, ILogger<UpdateUsers> _logger)
            : IRequestHandler<Command, Result<ulong, QueryStatus>>
        {
            public async Task<Result<ulong, QueryStatus>> Handle(Command request, CancellationToken cancellationToken)
            {
                _logger.LogInformation("Beginning UpdateUsers CSV Deserialization");

                using var csvReader = new CsvReader(new StringReader(request.UserCsv), CultureInfo.InvariantCulture);
                var users = csvReader.GetRecords<UserDto>().ToList();

                _logger.LogInformation("UpdateUsers CSV Deserialization succeeded");

                var guilds = await _context.Guilds
                    .Include(y => y.Users)
                    .ToListAsync();

                var usersDb = await _context.Users.ToListAsync();

                var guildEntity = guilds.FirstOrDefault(x => x.Id == request.GuildId);

                if (guildEntity is null)
                {
                    return QueryResult<ulong>.NotFound();
                }

                foreach (var user in users)
                {
                    _logger.LogInformation("Updating {user}", user);
                    var dbUser = usersDb.FirstOrDefault(x => x.Id == user.UserId);

                    if (dbUser is null)
                    {
                        _logger.LogInformation("Adding new {user}", user);
                        var userEntity = new User {Id = user.UserId, Name = user.Name};
                        _context.Users.Add(userEntity);

                        guildEntity.Users.Add(userEntity);
                    }
                    else if (!guildEntity.Users.Contains(dbUser))
                    {
                        _logger.LogInformation("Adding new user guild mapping {user}", user);
                        guildEntity.Users.Add(dbUser);
                    }
                }

                foreach (var user in guildEntity.Users
                    .Where(x => users.All(y => y.UserId != x.Id)))
                {
                    _context.Users.Remove(user);
                }

                _logger.LogInformation("Saving UpdateUser Changes");

                await _context.SaveChangesAsync();

                return QueryResult<ulong>.Success(request.GuildId);
            }
        }
    }
}
