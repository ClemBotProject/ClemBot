using System;
using System.Threading;
using System.Threading.Tasks;
using ClemBot.Api.Common.Utilities;
using ClemBot.Api.Data.Contexts;
using FluentValidation;
using MediatR;
using Microsoft.EntityFrameworkCore;

namespace ClemBot.Api.Core.Features.Tags;

public class Edit
{
    public class Validator : AbstractValidator<Command>
    {
        public Validator()
        {
            RuleFor(p => p.GuildId).NotNull();
            RuleFor(p => p.Name).NotNull();
        }
    }

    public class TagDto
    {
        public string Name { get; set; } = null!;

        public string Content { get; set; } = null!;

        public string CreationDate { get; set; } = null!;

        public ulong GuildId { get; set; }

        public ulong UserId { get; set; }

        public int UseCount { get; set; }
    }

    public class Command : IRequest<IQueryResult<TagDto>>
    {
        public ulong GuildId { get; set; }

        public string Name { get; set; } = null!;

        public string? Content { get; set; }

        public ulong? UserId { get; set; }
    }

    public record Handler(ClemBotContext _context) : IRequestHandler<Command, IQueryResult<TagDto>>
    {
        public async Task<IQueryResult<TagDto>> Handle(Command request, CancellationToken cancellationToken)
        {
            var tag = await _context.Tags
                .FirstOrDefaultAsync(g => g.GuildId == request.GuildId && g.Name == request.Name);

            if (tag is null)
            {
                return QueryResult<TagDto>.NotFound();
            }

            tag.Name = request.Name;
            tag.Content = request.Content ?? tag.Content;
            tag.UserId = request.UserId ?? tag.UserId;
            await _context.SaveChangesAsync();

            return QueryResult<TagDto>.Success(new TagDto()
            {
                Name = tag.Name,
                Content = tag.Content,
                CreationDate = tag.Time.ToDateTimeUnspecified().ToLongDateString(),
                GuildId = tag.GuildId,
                UserId = tag.UserId,
                UseCount = tag.TagUses.Count
            });
        }

    }
}
