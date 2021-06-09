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

        public class Command : IRequest<Result<Guild, QueryStatus>>
        {
            public ulong Id { get; set; }

            public string Name { get; set; } = null!;
        }

        public record Handler(ClemBotContext _context) : IRequestHandler<Command, Result<Guild, QueryStatus>>
        {
            public async Task<Result<Guild, QueryStatus>> Handle(Command request, CancellationToken cancellationToken)
            {
                var guild = new Guild
                {
                    Id = request.Id,
                    Name = request.Name
                };

                if (await _context.Guilds.Where(x => x.Id == guild.Id).AnyAsync())
                {
                    return QueryResult<Guild>.Conflict();
                }

                _context.Guilds.Add(guild);
                await _context.SaveChangesAsync();

                return QueryResult<Guild>.Success(guild);
            }
        }
    }
}
