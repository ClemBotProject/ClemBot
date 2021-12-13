using System;
using System.Threading;
using System.Threading.Tasks;
using ClemBot.Api.Common.Utilities;
using ClemBot.Api.Data.Contexts;
using ClemBot.Api.Data.Models;
using FluentValidation;
using MediatR;
using Microsoft.EntityFrameworkCore;

namespace ClemBot.Api.Core.Features.Tags.Bot;

public class Invoke
{
    public class Validator : AbstractValidator<Command>
    {
        public Validator()
        {
            RuleFor(p => p.GuildId).NotNull();
            RuleFor(p => p.Name).NotNull();
        }
    }
    public class Model
    {
        public ulong GuildId { get; init; }

        public string? Name { get; init; }
    }

    public class Command : IRequest<IQueryResult<Model>>
    {
        public string Name { get; set; } = null!;

        public ulong GuildId { get; set; }

        public ulong ChannelId { get; set; }

        public ulong UserId { get; set; }
    }

    public record Handler(ClemBotContext _context) : IRequestHandler<Command, IQueryResult<Model>>
    {
        public async Task<IQueryResult<Model>> Handle(Command request, CancellationToken cancellationToken)
        {
            var tag = await _context.Tags
                .FirstOrDefaultAsync(g => g.GuildId == request.GuildId && g.Name == request.Name);

            if (tag is null)
            {
                return QueryResult<Model>.NotFound();
            }
            tag.TagUses.Add(new TagUse()
            {
                ChannelId = request.ChannelId,
                UserId = request.UserId,
                Time = DateTime.UtcNow
            });
            await _context.SaveChangesAsync();

            return QueryResult<Model>.Success(new Model()
            {
                GuildId = tag.GuildId,
                Name = tag.Name
            });

        }
    }
}
