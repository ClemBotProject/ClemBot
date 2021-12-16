using System;
using System.Threading;
using System.Threading.Tasks;
using ClemBot.Api.Common;
using ClemBot.Api.Common.Security.Policies.GuildSandbox;
using ClemBot.Api.Common.Utilities;
using ClemBot.Api.Data.Contexts;
using ClemBot.Api.Data.Models;
using FluentValidation;
using MediatR;
using Microsoft.EntityFrameworkCore;
using NodaTime;
using NodaTime.Extensions;

namespace ClemBot.Api.Core.Features.Tags;

public class Create
{
    public class Validator : AbstractValidator<Command>
    {
        public Validator()
        {
            RuleFor(p => p.Name).NotEmpty().Must(c => !c.Any(char.IsWhiteSpace));
            RuleFor(p => p.Content).NotNull();
            RuleFor(p => p.GuildId).NotNull();
            RuleFor(p => p.UserId).NotNull();
        }
    }

    public class TagDto : IResponseModel
    {
        public string Name { get; set; } = null!;

        public string Content { get; set; } = null!;

        public string CreationDate { get; set; } = null!;

        public ulong GuildId { get; set; }

        public ulong UserId { get; set; }
    }

    public class Command : IGuildUserSandboxModel, IRequest<IQueryResult<TagDto>>
    {
        public string Name { get; set; } = null!;

        public string Content { get; set; } = null!;

        public LocalDateTime? Time { get; }

        public ulong GuildId { get; init; }

        public ulong UserId { get; init; }
    }

    public record Handler(ClemBotContext _context) : IRequestHandler<Command, IQueryResult<TagDto>>
    {
        public async Task<IQueryResult<TagDto>> Handle(Command request, CancellationToken cancellationToken)
        {
            if (await _context.Tags.FirstOrDefaultAsync(x => x.Guild.Id == request.GuildId && x.Name == request.Name) is not null)
            {
               return QueryResult<TagDto>.Conflict();
            }

            var tag = new Tag
            {
                Name = request.Name,
                Content = request.Content,
                Time = SystemClock.Instance.InZone(DateTimeZone.Utc).GetCurrentLocalDateTime(),
                GuildId = request.GuildId,
                UserId = request.UserId
            };

            _context.Tags.Add(tag);
            await _context.SaveChangesAsync();

            return QueryResult<TagDto>.Success(new TagDto
            {
                Name = tag.Name,
                Content = tag.Content,
                CreationDate = tag.Time.ToDateTimeUnspecified().ToLongDateString(),
                GuildId = tag.GuildId,
                UserId = tag.UserId
            });

        }
    }
}
