using ClemBot.Api.Common;
using ClemBot.Api.Common.Security.Policies.GuildSandbox;
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
            RuleFor(p => p.GuildId).NotNull();
            RuleFor(p => p.Message).NotNull();
        }
    }

    public record Command : IGuildSandboxModel, IRequest<IQueryResult<Model>>
    {
        public ulong GuildId { get; init; }

        public string Message { get; set; } = null!;
    }

    public record Model : IResponseModel
    {
        public ulong Id { get; init; }
    }

    public record Handler(ClemBotContext _context) : IRequestHandler<Command, IQueryResult<Model>>
    {
        public async Task<IQueryResult<Model>> Handle(Command request, CancellationToken cancellationToken)
        {
            var guild = await _context.Guilds.FirstOrDefaultAsync(x => x.Id == request.GuildId);

            if (guild is null)
            {
                return QueryResult<Model>.NotFound();
            }

            guild.WelcomeMessage = request.Message;
            await _context.SaveChangesAsync();

            return QueryResult<Model>.Success(new Model { Id = guild.Id});
        }
    }
}
