using System.Collections.Generic;
using System.Linq;
using System.Threading;
using System.Threading.Tasks;
using ClemBot.Api.Core.Utilities;
using ClemBot.Api.Data.Contexts;
using ClemBot.Api.Data.Models;
using FluentValidation;
using MediatR;
using Microsoft.EntityFrameworkCore;

namespace ClemBot.Api.Core.Features.Guilds.Bot
{
    public class UpdateUsers
    {
        public class UserDto
        {
            public ulong UserId { get; set; }

            public string? Name { get; set; }
        }

        public record GuildDto
        {
            public ulong GuildId { get; init; }

            public IReadOnlyList<UserDto> Users { get; set; } = new List<UserDto>();
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
                    .Include(y => y.Users)
                    .ToListAsync();

                var users = await _context.Users.ToListAsync();

                foreach (var guild in request.Guilds)
                {
                    var guildEntity = guilds.FirstOrDefault(x => x.Id == guild.GuildId);

                    if (guildEntity is null)
                    {
                        continue;
                    }

                    foreach (var user in guild.Users)
                    {
                        var dbUser = users.FirstOrDefault(x => x.Id == user.UserId);

                        if (dbUser is null)
                        {
                            var userEntity = new User {Id = user.UserId, Name = user.Name};
                            _context.Users.Add(userEntity);

                            guildEntity.Users.Add(userEntity);
                        }
                        else if (!guildEntity.Users.Contains(dbUser))
                        {
                            guildEntity.Users.Add(dbUser);
                        }
                    }

                    foreach (var user in guildEntity.Users
                        .Where(x => guild.Users.All(y => y.UserId != x.Id)))
                    {
                        _context.Users.Remove(user);
                    }
                }


                await _context.SaveChangesAsync();

                return QueryResult<IEnumerable<ulong>>.Success(request.Guilds.Select(x => x.GuildId));
            }
        }
    }
}
