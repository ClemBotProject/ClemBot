using ClemBot.Api.Common;
using ClemBot.Api.Data.Contexts;
using FluentValidation;
using Microsoft.EntityFrameworkCore;

namespace ClemBot.Api.Core.Features.Tags.Bot;

public class Search
{
    private const float _minimumNameSimilarity = 0.1f;

    public class Validator : AbstractValidator<Command>
    {
        public Validator()
        {
            RuleFor(p => p.GuildId).NotNull();
            RuleFor(p => p.Query).NotNull();
            RuleFor(p => p.Limit).LessThanOrEqualTo(32).GreaterThan(0);
        }
    }

    public class Command : IRequest<QueryResult<Model>>
    {
        public string Query { get; init; } = null!;

        public ulong GuildId { get; init; }

        public int Limit { get; init; } = 5;
    }

    public class Tag
    {
        public string Name { get; init; } = null!;

        public string Content { get; init; } = null!;

        public string CreationDate { get; init; } = null!;

        public ulong GuildId { get; init; }

        public ulong UserId { get; init; }

        public string UserName { get; init; } = null!;

        public int UseCount { get; init; }
    }

    public class Model : IResponseModel
    {
        public IEnumerable<Tag> Tags { get; init; } = null!;
    }

    public record Handler(ClemBotContext _context) : IRequestHandler<Command, QueryResult<Model>>
    {
        public async Task<QueryResult<Model>> Handle(Command request, CancellationToken cancellationToken)
        {
            var tags = await _context.Tags
                .Where(t => t.GuildId == request.GuildId)
                .Select(t => new {t, Similarity=EF.Functions.TrigramsSimilarity(t.Name, request.Query)})
                .Where(e => e.Similarity > _minimumNameSimilarity)
                .OrderByDescending(e => e.Similarity)
                .Select(e => e.t)
                .Take(request.Limit)
                .Include(t => t.TagUses)
                .Include(t => t.User)
                .ToListAsync(cancellationToken);

            return QueryResult<Model>.Success(new Model()
            {
                Tags = tags.Select(tag => new Tag()
                {
                    Name = tag.Name,
                    Content = tag.Content,
                    CreationDate = tag.Time.ToDateTimeUnspecified().ToLongDateString(),
                    UserId = tag.UserId,
                    UserName = tag.User.Name,
                    GuildId = tag.GuildId,
                    UseCount = tag.TagUses.Count
                })
            });
        }
    }
}
