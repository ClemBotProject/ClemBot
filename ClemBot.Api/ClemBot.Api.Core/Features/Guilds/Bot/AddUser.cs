using ClemBot.Api.Data.Contexts;
using ClemBot.Api.Data.Models;
using FluentValidation;
using Microsoft.EntityFrameworkCore;

namespace ClemBot.Api.Core.Features.Guilds.Bot;

public class AddUser
{
    public class Validator : AbstractValidator<Command>
    {
        public Validator()
        {
            RuleFor(p => p.GuildId).NotNull();
            RuleFor(p => p.UserId).NotNull();
        }
    }

    public class Command : IRequest<IQueryResult<ulong>>
    {
        public ulong GuildId { get; set; }

        public ulong UserId { get; set; }
    }

    public record Handler(ClemBotContext _context) : IRequestHandler<Command, IQueryResult<ulong>>
    {
        public async Task<IQueryResult<ulong>> Handle(Command request, CancellationToken cancellationToken)
        {
            if (!await _context.Guilds.AnyAsync(x => x.Id == request.GuildId))
            {
                return QueryResult<ulong>.NotFound();
            }

            if (await _context.GuildUser.AnyAsync(x => x.GuildId == request.GuildId && x.UserId == request.UserId))
            {
                return QueryResult<ulong>.Conflict();
            }

            _context.GuildUser.Add(new GuildUser
            {
                GuildId = request.GuildId,
                UserId = request.UserId
            });

            await _context.SaveChangesAsync();

            return QueryResult<ulong>.Success(request.GuildId);
        }
    }
}
