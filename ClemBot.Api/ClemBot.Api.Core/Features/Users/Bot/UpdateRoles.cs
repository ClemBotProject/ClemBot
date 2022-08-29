using ClemBot.Api.Data.Contexts;
using ClemBot.Api.Data.Models;
using ClemBot.Api.Services.Caching.Users.Models;
using FluentValidation;
using Microsoft.EntityFrameworkCore;

namespace ClemBot.Api.Core.Features.Users.Bot;

public class UpdateRoles
{
    public class Validator : AbstractValidator<Command>
    {
        public Validator()
        {
            RuleFor(p => p.Id).NotNull();
        }
    }

    public record Command : IRequest<QueryResult<IEnumerable<ulong>>>
    {
        public ulong Id { get; init; }

        public ulong GuildId { get; init; }

        public List<ulong> Roles { get; init; } = new();
    }

    public class Handler : IRequestHandler<Command, QueryResult<IEnumerable<ulong>>>
    {
        private ClemBotContext _context { get; }
        private IMediator _mediator { get; }

        public Handler(ClemBotContext context, IMediator mediator)
        {
            _context = context;
            _mediator = mediator;
        }

        public async Task<QueryResult<IEnumerable<ulong>>> Handle(Command request, CancellationToken cancellationToken)
        {
            if (!await _mediator.Send(new UserExistsRequest{ Id = request.Id }))
            {
                return QueryResult<IEnumerable<ulong>>.NotFound();
            }

            var roleMappings = await _context.RoleUser
                .Where(ru => ru.UserId == request.Id && ru.Role.GuildId == request.GuildId)
                .ToListAsync();

            var oldRoleMappings = roleMappings.Where(ru => !request.Roles.Contains(ru.RoleId));

            var newRoleMappings = request.Roles
                .Where(r => roleMappings.All(ru => ru.RoleId != r))
                .Select(r => new RoleUser { RoleId = r, UserId = request.Id });

            _context.RoleUser.RemoveRange(oldRoleMappings);
            _context.RoleUser.AddRange(newRoleMappings);

            await _context.SaveChangesAsync();

            return QueryResult<IEnumerable<ulong>>.Success(request.Roles);
        }
    }
}
