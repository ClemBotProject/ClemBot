using System;
using System.Linq;
using System.Threading;
using System.Threading.Tasks;
using ClemBot.Api.Common.Enums;
using ClemBot.Api.Common.Utilities;
using ClemBot.Api.Data.Contexts;
using ClemBot.Api.Data.Models;
using FluentValidation;
using MediatR;
using Microsoft.EntityFrameworkCore;

namespace ClemBot.Api.Core.Features.ClaimMappings.Bot;

public class Delete
{
    public class Validator : AbstractValidator<Command>
    {
        public Validator()
        {
            RuleFor(p => p.Claim).NotNull();
            RuleFor(p => p.RoleId).NotNull();
        }
    }

    public class Command : IRequest<IQueryResult<ulong>>
    {
        public BotAuthClaims Claim { get; set; }

        public ulong RoleId { get; set; }
    }

    public record Handler(ClemBotContext _context) : IRequestHandler<Command, IQueryResult<ulong>>
    {
        public async Task<IQueryResult<ulong>> Handle(Command request, CancellationToken cancellationToken)
        {
            var claimMapping = new ClaimsMapping
            {
                Claim = request.Claim,
                RoleId = request.RoleId
            };

            var role = await _context.Roles.FirstOrDefaultAsync(x => x.Id == request.RoleId);

            if (role is null)
            {
                return QueryResult<ulong>.NotFound();
            }

            var dbClaim = await _context.ClaimsMappings
                .FirstOrDefaultAsync(x => x.RoleId == request.RoleId && x.Claim == request.Claim);

            if (dbClaim is null)
            {
                return QueryResult<ulong>.NotFound();
            }

            role.Claims.Remove(dbClaim);
            await _context.SaveChangesAsync();

            return QueryResult<ulong>.Success(request.RoleId);

        }
    }
}
