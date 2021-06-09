using System;
using System.Threading;
using System.Threading.Tasks;
using ClemBot.Api.Core.Utilities;
using ClemBot.Api.Data.Contexts;
using ClemBot.Api.Data.Models;
using FluentValidation;
using MediatR;

namespace ClemBot.Api.Core.Features.Messages.Bot
{
    public class Create
    {
        public class Validator : AbstractValidator<Command>
        {
            public Validator()
            {
                RuleFor(p => p.Id).NotNull();
                RuleFor(p => p.Content).NotNull();
                RuleFor(p => p.GuildId).NotNull();
                RuleFor(p => p.ChannelId).NotNull();
                RuleFor(p => p.UserId).NotNull();
            }
        }

        public class Command : IRequest<Result<ulong, QueryStatus>>
        {
            public ulong Id { get; set; }

            public string Content { get; set; } = null!;

            public DateTime Time { get; } = DateTime.UtcNow;

            public ulong GuildId { get; set; }

            public ulong ChannelId { get; set; }

            public ulong UserId { get; set; }
        }

        public record Handler(ClemBotContext _context) : IRequestHandler<Command, Result<ulong, QueryStatus>>
        {
            public async Task<Result<ulong, QueryStatus>> Handle(Command request, CancellationToken cancellationToken)
            {
                var message = new Message()
                {
                    Id = request.Id,
                    GuildId = request.GuildId,
                    UserId = request.UserId,
                    ChannelId = request.ChannelId
                };

                message.Contents.Add(new MessageContent()
                {
                    MessageId = message.Id,
                    Time = DateTime.UtcNow,
                    Content = request.Content
                });

                _context.Messages.Add(message);
                await _context.SaveChangesAsync();

                return QueryResult<ulong>.Success(request.Id);

            }
        }
    }
}
