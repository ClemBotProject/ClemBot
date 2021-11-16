using System;
using System.Collections.Generic;
using System.Threading;
using System.Threading.Tasks;
using ClemBot.Api.Core.Utilities;
using ClemBot.Api.Data.Contexts;
using ClemBot.Api.Data.Models;
using ClemBot.Api.Services.Messages.Models;
using FluentValidation;
using MediatR;
using Microsoft.EntityFrameworkCore;
using NodaTime.Text;

namespace ClemBot.Api.Core.Features.Messages.Bot;

public class Edit
{
    public class MessageEditDto
    {
        public ulong Id { get; set; }

        public string Content { get; set; } = null!;

        public string Time { get; set; } = null!;
    }

    public class Command : IRequest<Result<IEnumerable<ulong>, QueryStatus>>
    {
        public List<MessageEditDto> Messages { get; set; } = null!;
    }

    public record Handler(ClemBotContext _context, IMediator _mediator) : IRequestHandler<Command, Result<IEnumerable<ulong>, QueryStatus>>
    {
        public async Task<Result<IEnumerable<ulong>, QueryStatus>> Handle(Command request, CancellationToken cancellationToken)
        {
            List<ulong> sentEditIds = new();

            foreach (var message in request.Messages)
            {
                if (!await _mediator.Send(new MessageExistsRequest { Id = message.Id }))
                {
                    continue;
                }

                var time = LocalDateTimePattern.ExtendedIso.Parse(message.Time).Value;

                _context.MessageContents.Add(new MessageContent
                {
                    MessageId = message.Id,
                    Content = message.Content,
                    Time = time
                });

                sentEditIds.Add(message.Id);
            }

            await _context.SaveChangesAsync();

            return QueryResult<IEnumerable<ulong>>.Success(sentEditIds);
        }
    }
}