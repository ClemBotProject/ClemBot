using System.Linq;
using System.Threading;
using System.Threading.Tasks;
using ClemBot.Api.Common.Utilities;
using ClemBot.Api.Data.Contexts;
using ClemBot.Api.Data.Models;
using FluentValidation;
using MediatR;
using Microsoft.EntityFrameworkCore;

namespace ClemBot.Api.Core.Features.Guilds.Bot;

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

    public class Command : IRequest<IQueryResult<Guild>>
    {
        public ulong Id { get; set; }

        public string Name { get; set; } = null!;

        public ulong OwnerId { get; set; }
    }

    public record Handler(ClemBotContext _context) : IRequestHandler<Command, IQueryResult<Guild>>
    {
        public async Task<IQueryResult<Guild>> Handle(Command request, CancellationToken cancellationToken)
        {
            var guild = new Guild
            {
                Id = request.Id,
                Name = request.Name,
                OwnerId = request.OwnerId
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
