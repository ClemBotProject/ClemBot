using System.Linq;
using System.Threading;
using System.Threading.Tasks;
using ClemBot.Api.Core.Utilities;
using ClemBot.Api.Data.Contexts;
using ClemBot.Api.Data.Models;
using FluentValidation;
using MediatR;
using Microsoft.EntityFrameworkCore;

namespace ClemBot.Api.Core.Features.Roles.Bot
{
    public class Create
    {
        public class Validator : AbstractValidator<Command>
        {
            public Validator()
            {
                RuleFor(p => p.Id).NotNull();
                RuleFor(p => p.Name).NotNull();
            }
        }

        public class Command : IRequest<Result<ulong, QueryStatus>>
        {
            public ulong Id { get; set; }

            public string Name { get; set; } = null!;

            public ulong GuildId { get; set; }
        }

        public record Handler(ClemBotContext _context) : IRequestHandler<Command, Result<ulong, QueryStatus>>
        {
            public async Task<Result<ulong, QueryStatus>> Handle(Command request, CancellationToken cancellationToken)
            {
                var role = new Role()
                {
                    Id = request.Id,
                    Name = request.Name,
                    GuildId = request.GuildId
                };

                if (await _context.Roles.Where(x => x.Id == role.Id).AnyAsync())
                {
                    return QueryResult<ulong>.Conflict();
                }

                _context.Roles.Add(role);
                await _context.SaveChangesAsync();

                return QueryResult<ulong>.Success(role.Id);
            }
        }
    }
}
