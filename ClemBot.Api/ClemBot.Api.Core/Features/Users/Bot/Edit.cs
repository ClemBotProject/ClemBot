using System.Threading;
using System.Threading.Tasks;
using ClemBot.Api.Core.Utilities;
using ClemBot.Api.Data.Contexts;
using FluentValidation;
using MediatR;
using Microsoft.EntityFrameworkCore;

namespace ClemBot.Api.Core.Features.Users.Bot
{
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

        public class Command : IRequest<Result<ulong, QueryStatus>>

        {
            public ulong Id { get; set; }

            public string Name { get; set; } = null!;
        }

        public record Handler(ClemBotContext _context) : IRequestHandler<Command, Result<ulong, QueryStatus>>
        {
            public async Task<Result<ulong, QueryStatus>> Handle(Command request, CancellationToken cancellationToken)
            {
                var user = await _context.Users
                   .FirstOrDefaultAsync(g => g.Id == request.Id);

                if (user is null)
                {
                    return QueryResult<ulong>.NotFound();
                }

                user.Name = request.Name;
                await _context.SaveChangesAsync();

                return QueryResult<ulong>.Success(user.Id);
            }
        }
    }
}
