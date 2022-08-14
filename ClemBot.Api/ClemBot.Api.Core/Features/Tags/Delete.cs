using System.Threading;
using System.Threading.Tasks;
using ClemBot.Api.Common.Utilities;
using ClemBot.Api.Data.Contexts;
using MediatR;
using Microsoft.EntityFrameworkCore;

namespace ClemBot.Api.Core.Features.Tags;

public class Delete
{
    public class Command : IRequest<QueryResult<Model>>
    {
        public ulong GuildId { get; set; }

        public string Name { get; set; } = null!;
    }

    public class Model
    {
        public ulong Id { get; init; }

        public string? Name { get; init; }

        public string? Content { get; init; }
    }

    public record QueryHandler(ClemBotContext _context) : IRequestHandler<Command, QueryResult<Model>>
    {
        public async Task<QueryResult<Model>> Handle(Command request, CancellationToken cancellationToken)
        {
            var tag = await _context.Tags
                .FirstOrDefaultAsync(g => g.GuildId == request.GuildId && g.Name == request.Name);

            if (tag is null)
            {
                return QueryResult<Model>.NotFound();
            }

            _context.Tags.Remove(tag);

            await _context.SaveChangesAsync();

            return QueryResult<Model>.Success(new Model()
            {
                Id = tag.GuildId,
                Name = tag.Name,
                Content = tag.Content
            });
        }
    }
}
