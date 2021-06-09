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
    public class GetWelcomeMessage
    {
        public class Validator : AbstractValidator<Command>
        {
            public Validator()
            {
                RuleFor(p => p.Id).NotNull();
            }
        }

        public record Command : IRequest<Result<string, QueryStatus>>
        {
            public ulong Id { get; set; }
        }

        public record Handler(ClemBotContext _context) : IRequestHandler<Command, Result<string, QueryStatus>>
        {
            public async Task<Result<string, QueryStatus>> Handle(Command request, CancellationToken cancellationToken)
            {
                var guild = await _context.Guilds.FirstOrDefaultAsync(x => x.Id == request.Id);

                if (guild is null)
                {
                    return QueryResult<string>.NotFound();
                }

                return QueryResult<string>.Success(guild.WelcomeMessage);
            }
        }
    }
}
