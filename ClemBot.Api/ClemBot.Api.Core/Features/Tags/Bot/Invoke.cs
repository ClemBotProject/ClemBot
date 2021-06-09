using System;
using System.Threading;
using System.Threading.Tasks;
using ClemBot.Api.Core.Utilities;
using ClemBot.Api.Data.Contexts;
using ClemBot.Api.Data.Models;
using FluentValidation;
using MediatR;
using Microsoft.EntityFrameworkCore;

namespace ClemBot.Api.Core.Features.Tags.Bot
{
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
            public ulong Id { get; init; }

            public string? Name { get; init; }
        }

        public class Command : IRequest<Result<Model, QueryStatus>>
        {
            public string Name { get; set; } = null!;

            public ulong GuildId { get; set; }

            public ulong ChannelId { get; set; }

            public ulong UserId { get; set; }
        }

        public record Handler(ClemBotContext _context) : IRequestHandler<Command, Result<Model, QueryStatus>>
        {
            public async Task<Result<Model, QueryStatus>> Handle(Command request, CancellationToken cancellationToken)
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
                    Id = tag.GuildId,
                    Name = tag.Name
                });

            }
        }
    }
}
