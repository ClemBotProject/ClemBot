using ClemBot.Api.Common;
using ClemBot.Api.Data.Contexts;
using FluentValidation;
using Microsoft.EntityFrameworkCore;

namespace ClemBot.Api.Core.Features.Guilds;

public class GetWelcomeMessage
{
    public class Validator : AbstractValidator<Command>
    {
        public Validator()
        {
            RuleFor(p => p.GuildId).NotNull();
        }
    }

    public record Command : IGuildSandboxModel, IRequest<QueryResult<Model>>
    {
        public ulong GuildId { get; init; }
    }

    public record Model : IResponseModel
    {
       public string? Message { get; init; }
    }

    public record Handler(ClemBotContext _context) : IRequestHandler<Command, QueryResult<Model>>
    {
        public async Task<QueryResult<Model>> Handle(Command request, CancellationToken cancellationToken)
        {
            var guild = await _context.Guilds
                .Select(x => new{ x.Id, x.WelcomeMessage })
                .FirstOrDefaultAsync(x => x.Id == request.GuildId);

            if (guild is null)
            {
                return QueryResult<Model>.NotFound();
            }

            return QueryResult<Model>.Success(new Model{ Message = guild.WelcomeMessage });
        }
    }
}
