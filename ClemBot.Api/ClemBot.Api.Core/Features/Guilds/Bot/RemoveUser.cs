using System.Linq;
using System.Threading;
using System.Threading.Tasks;
using ClemBot.Api.Common.Utilities;
using ClemBot.Api.Data.Contexts;
using ClemBot.Api.Data.Models;
using FluentValidation;
using LinqToDB;
using MediatR;
using Microsoft.EntityFrameworkCore;

namespace ClemBot.Api.Core.Features.Guilds.Bot;

public class RemoveUser
{
    public class Validator : AbstractValidator<Command>
    {
        public Validator()
        {
            RuleFor(p => p.GuildId).NotNull();
            RuleFor(p => p.UserId).NotNull();
        }
    }

    public class Command : IRequest<IQueryResult<ulong>>
    {
        public ulong GuildId { get; set; }

        public ulong UserId { get; set; }
    }

    public record Handler(ClemBotContext _context) : IRequestHandler<Command, IQueryResult<ulong>>
    {
        public async Task<IQueryResult<ulong>> Handle(Command request, CancellationToken cancellationToken)
        {
            await _context.RoleUser
                .Where(u => u.UserId == request.UserId && u.Role.GuildId == request.GuildId)
                .DeleteAsync();

            await _context.GuildUser
                .Where(u => u.UserId == request.UserId && u.GuildId == request.GuildId)
                .DeleteAsync();

            return QueryResult<ulong>.Success(request.GuildId);
        }
    }
}
