using System.Threading;
using System.Threading.Tasks;
using ClemBot.Api.Core.Utilities;
using ClemBot.Api.Data.Contexts;
using FluentValidation;
using MediatR;
using Microsoft.EntityFrameworkCore;

namespace ClemBot.Api.Core.Features.Tags
{
    public class Edit
    {
        public class Validator : AbstractValidator<Command>
        {
            public Validator()
            {
                RuleFor(p => p.GuildId).NotNull();
                RuleFor(p => p.Name).NotNull();
                RuleFor(p => p.Content).NotNull();
            }
        }

        public class TagDto
        {
            public string Name { get; set; } = null!;

            public string Content { get; set; } = null!;
        }

        public class Command : IRequest<Result<TagDto, QueryStatus>>
        {
            public ulong GuildId { get; set; }

            public string Name { get; set; } = null!;

            public string Content { get; set; } = null!;
        }

        public record Handler(ClemBotContext _context) : IRequestHandler<Command, Result<TagDto, QueryStatus>>
        {
            public async Task<Result<TagDto, QueryStatus>> Handle(Command request, CancellationToken cancellationToken)
            {
                var tag = await _context.Tags
                   .FirstOrDefaultAsync(g => g.GuildId == request.GuildId && g.Name == request.Name);

                if (tag is null)
                {
                    return QueryResult<TagDto>.NotFound();
                }

                tag.Content = request.Content;
                await _context.SaveChangesAsync();

                return QueryResult<TagDto>.Success(new TagDto()
                {
                    Name = tag.Name,
                    Content = tag.Content
                });
            }

        }
    }
}
