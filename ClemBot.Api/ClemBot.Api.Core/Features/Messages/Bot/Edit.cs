using System;
using System.Threading;
using System.Threading.Tasks;
using ClemBot.Api.Core.Utilities;
using ClemBot.Api.Data.Contexts;
using ClemBot.Api.Data.Models;
using FluentValidation;
using MediatR;
using Microsoft.EntityFrameworkCore;

namespace ClemBot.Api.Core.Features.Messages.Bot
{
    public class Edit
    {
        public class Validator : AbstractValidator<Command>
        {
            public Validator()
            {
                RuleFor(p => p.Id).NotNull();
                RuleFor(p => p.Content).NotNull();
            }
        }

        public class Command : IRequest<Result<ulong, QueryStatus>>
        {
            public ulong Id { get; set; }

            public string Content { get; set; } = null!;
        }

        public record Handler(ClemBotContext _context) : IRequestHandler<Command, Result<ulong, QueryStatus>>
        {
            public async Task<Result<ulong, QueryStatus>> Handle(Command request, CancellationToken cancellationToken)
            {
                var message = await _context.Messages
                   .FirstOrDefaultAsync(g => g.Id == request.Id);

                if (message is null)
                {
                    return QueryResult<ulong>.NotFound();
                }

                message.Contents.Add(new MessageContent()
                {
                    MessageId = message.Id,
                    Content = request.Content,
                    Time = DateTime.UtcNow
                });

                await _context.SaveChangesAsync();

                return QueryResult<ulong>.Success(message.Id);
            }

        }
    }
}
