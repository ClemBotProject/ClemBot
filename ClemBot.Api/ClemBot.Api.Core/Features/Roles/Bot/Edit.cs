using System.Threading;
using System.Threading.Tasks;
using ClemBot.Api.Common.Utilities;
using ClemBot.Api.Data.Contexts;
using FluentValidation;
using MediatR;
using Microsoft.EntityFrameworkCore;

namespace ClemBot.Api.Core.Features.Roles.Bot;

public class Edit
{
    public class Validator : AbstractValidator<Command>
    {
        public Validator()
        {
            RuleFor(p => p.Id).NotNull();
        }
    }

    public class Command : IRequest<IQueryResult<ulong>>
    {
        public ulong Id { get; set; }

        public string? Name { get; set; } = null;

        public bool? Admin { get; set; } = null;

        public bool? Assignable { get; set; } = null;
    }

    public record Handler(ClemBotContext _context) : IRequestHandler<Command, IQueryResult<ulong>>
    {
        public async Task<IQueryResult<ulong>> Handle(Command request, CancellationToken cancellationToken)
        {
            var role = await _context.Roles
                .FirstOrDefaultAsync(g => g.Id == request.Id);

            if (role is null)
            {
                return QueryResult<ulong>.NotFound();
            }

            role.Name = request.Name ?? role.Name;
            role.Admin = request.Admin ?? role.Admin;
            role.IsAssignable = request.Assignable ?? role.IsAssignable;

            await _context.SaveChangesAsync();

            return QueryResult<ulong>.Success(role.Id);
        }
    }
}
