using System.Linq;
using System.Threading;
using System.Threading.Tasks;
using ClemBot.Api.Core.Utilities;
using ClemBot.Api.Data.Contexts;
using FluentValidation;
using MediatR;
using Microsoft.EntityFrameworkCore;

namespace ClemBot.Api.Core.Features.Guilds.Bot
{
    public class DeleteWelcomeMessage
    {
        public class Validator : AbstractValidator<Command>
        {
            public Validator()
            {
                RuleFor(p => p.Id).NotNull();
            }
        }

        public record Command : IRequest<Result<ulong, QueryStatus>>
        {
            public ulong Id { get; set; }
        }

        public record Handler(ClemBotContext _context) : IRequestHandler<Command, Result<ulong, QueryStatus>>
        {
            public async Task<Result<ulong, QueryStatus>> Handle(Command request, CancellationToken cancellationToken)
            {
                var guild = await _context.Guilds.FirstOrDefaultAsync(x => x.Id == request.Id);

                if (guild is null)
                {
                    return QueryResult<ulong>.NotFound();
                }

                guild.WelcomeMessage = null;
                await _context.SaveChangesAsync();

                return QueryResult<ulong>.Success(guild.Id);
            }
        }
    }
}
