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

namespace ClemBot.Api.Core.Features.Users.Bot;

public class CreateBulk
{
    public class UserDto
    {
        public ulong Id { get; set; }

        public string Name { get; set; } = null!;
    }

    public class Command : IRequest<IQueryResult<IEnumerable<ulong>>>
    {
        public List<UserDto> Users { get; set; } = new();
    }

    public record Handler(ClemBotContext _context) : IRequestHandler<Command, IQueryResult<IEnumerable<ulong>>>
    {
        public async Task<IQueryResult<IEnumerable<ulong>>> Handle(Command request, CancellationToken cancellationToken)
        {
            var dbUsers = await _context.Users.ToListAsync();

            var newUsers = request.Users
                .Where(x => dbUsers.All(y => y.Id != x.Id))
                .ToList();

            foreach (var user in newUsers)
            {
                var userEntity = new User()
                {
                    Id = user.Id,
                    Name = user.Name
                };
                _context.Users.Add(userEntity);
            }

            await _context.SaveChangesAsync();

            return QueryResult<IEnumerable<ulong>>.Success(newUsers.Select(x => x.Id));
        }
    }
}
