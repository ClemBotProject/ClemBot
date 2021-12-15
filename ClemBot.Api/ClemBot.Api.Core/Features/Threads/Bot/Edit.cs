using System.Threading;
using System.Threading.Tasks;
using ClemBot.Api.Common.Utilities;
using ClemBot.Api.Data.Contexts;
using FluentValidation;
using MediatR;
using Microsoft.EntityFrameworkCore;

namespace ClemBot.Api.Core.Features.Threads.Bot;

public class Edit
{
    public class Validator : AbstractValidator<Command>
    {
        public Validator()
        {
            RuleFor(p => p.Id).NotNull();
            RuleFor(p => p.Name).NotNull();
        }
    }

    public class Command : IRequest<IQueryResult<ulong>>

    {
        public ulong Id { get; set; }

        public string Name { get; set; } = null!;
    }

    public record Handler(ClemBotContext _context) : IRequestHandler<Command, IQueryResult<ulong>>
    {
        public async Task<IQueryResult<ulong>> Handle(Command request, CancellationToken cancellationToken)
        {
            var channel = await _context.Channels
                .FirstOrDefaultAsync(g => g.Id == request.Id);

            if (channel is null)
            {
                return QueryResult<ulong>.NotFound();
            }

            channel.Name = request.Name;
            await _context.SaveChangesAsync();

            return QueryResult<ulong>.Success(channel.Id);
        }
    }
}
