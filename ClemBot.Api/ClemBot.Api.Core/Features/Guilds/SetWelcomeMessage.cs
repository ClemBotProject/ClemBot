using ClemBot.Api.Data.Contexts;
using FluentValidation;
using Microsoft.EntityFrameworkCore;

namespace ClemBot.Api.Core.Features.Guilds;

public class SetWelcomeMessage
{
    public class Validator : AbstractValidator<Command>
    {
        public Validator()
        {
            RuleFor(p => p.Id).NotNull();
            RuleFor(p => p.Message).NotNull();
        }
    }

    public record Command : IRequest<IQueryResult<ulong>>
    {
        public ulong Id { get; set; }
        public string Message { get; set; } = null!;
    }

    public record Handler(ClemBotContext _context) : IRequestHandler<Command, IQueryResult<ulong>>
    {
        public async Task<IQueryResult<ulong>> Handle(Command request, CancellationToken cancellationToken)
        {
            var guild = await _context.Guilds.FirstOrDefaultAsync(x => x.Id == request.Id);

            if (guild is null)
            {
                return QueryResult<ulong>.NotFound();
            }

            guild.WelcomeMessage = request.Message;
            await _context.SaveChangesAsync();

            return QueryResult<ulong>.Success(guild.Id);
        }
    }
}
