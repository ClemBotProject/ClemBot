using System;
using System.Linq;
using System.Threading;
using System.Threading.Tasks;
using ClemBot.Api.Core.Utilities;
using ClemBot.Api.Data.Contexts;
using ClemBot.Api.Data.Models;
using FluentValidation;
using MediatR;
using Microsoft.EntityFrameworkCore;

namespace ClemBot.Api.Core.Features.CustomPrefixes.Bot
{
    public class Add
    {
        public class Validator : AbstractValidator<Command>
        {
            public Validator()
            {
                RuleFor(p => p.GuildId).NotNull();
                RuleFor(p => p.Prefix).NotNull();
            }
        }

        public class Command : IRequest<Result<ulong, QueryStatus>>
        {
            public ulong GuildId { get; set; }

            public string Prefix { get; set; } = null!;
        }

        public record Handler(ClemBotContext _context) : IRequestHandler<Command, Result<ulong, QueryStatus>>
        {
            public async Task<Result<ulong, QueryStatus>> Handle(Command request, CancellationToken cancellationToken)
            {
                var guild = await _context.Guilds
                    .Include(x => x.CustomPrefixes)
                    .FirstOrDefaultAsync(g => g.Id == request.GuildId);

                if (guild is null)
                {
                    return QueryResult<ulong>.NotFound();
                }

                var prefix = new CustomPrefix()
                {
                    GuildId = request.GuildId,
                    Prefix = request.Prefix
                };

                guild.CustomPrefixes.Clear();
                guild.CustomPrefixes.Add(prefix);

                await _context.SaveChangesAsync();

                return QueryResult<ulong>.Success(request.GuildId);
            }
        }
    }
}
