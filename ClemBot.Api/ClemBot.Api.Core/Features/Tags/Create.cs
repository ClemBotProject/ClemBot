using System;
using System.Threading;
using System.Threading.Tasks;
using ClemBot.Api.Core.Utilities;
using ClemBot.Api.Data.Contexts;
using ClemBot.Api.Data.Models;
using FluentValidation;
using MediatR;

namespace ClemBot.Api.Core.Features.Tags
{
    public class Create
    {
        public class Validator : AbstractValidator<Command>
        {
            public Validator()
            {
                RuleFor(p => p.Name).NotNull();
                RuleFor(p => p.Content).NotNull();
                RuleFor(p => p.GuildId).NotNull();
                RuleFor(p => p.UserId).NotNull();
            }
        }

        public class TagDto
        {
            public string Name { get; set; } = null!;

            public string Content { get; set; } = null!;
        }

        public class Command : IRequest<Result<TagDto, QueryStatus>>
        {
            public string Name { get; set; } = null!;

            public string Content { get; set; } = null!;

            public DateTime Time { get; }

            public ulong GuildId { get; set; }

            public ulong UserId { get; set; }
        }

        public record Handler(ClemBotContext _context) : IRequestHandler<Command, Result<TagDto, QueryStatus>>
        {
            public async Task<Result<TagDto, QueryStatus>> Handle(Command request, CancellationToken cancellationToken)
            {
                var tag = new Tag()
                {
                    Name = request.Name,
                    Content = request.Content,
                    Time = DateTime.UtcNow,
                    GuildId = request.GuildId,
                    UserId = request.UserId
                };

                _context.Tags.Add(tag);
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
