using System;
using System.Collections.Generic;
using System.Globalization;
using System.Threading;
using System.Threading.Tasks;
using ClemBot.Api.Common.Utilities;
using ClemBot.Api.Data.Contexts;
using ClemBot.Api.Data.Models;
using ClemBot.Api.Services.Caching.Channels.Models;
using ClemBot.Api.Services.Caching.Guilds.Models;
using ClemBot.Api.Services.Caching.Users.Models;
using NodaTime.Text;
using FluentValidation;
using MediatR;

namespace ClemBot.Api.Core.Features.Messages.Bot;

public class Create
{
    public class MessageDto
    {
        public ulong Id { get; set; }

        public string Content { get; set; } = null!;

        public string Time { get; set; } = null!;

        public ulong GuildId { get; set; }

        public ulong ChannelId { get; set; }

        public ulong UserId { get; set; }
    }

    public class Command : IRequest<IQueryResult<IEnumerable<ulong>>>
    {
        public List<MessageDto> Messages { get; set; } = null!;
    }

    public record Handler(ClemBotContext _context, IMediator _mediator)
        : IRequestHandler<Command, IQueryResult<IEnumerable<ulong>>>
    {
        public async Task<IQueryResult<IEnumerable<ulong>>> Handle(Command request, CancellationToken cancellationToken)
        {
            List<ulong> createdMessageIds = new();

            foreach (var messageDto in request.Messages)
            {
                if (!await _mediator.Send(new UserExistsRequest { Id = messageDto.UserId }))
                {
                    continue;
                }

                if (!await _mediator.Send(new GuildExistsRequest{ Id = messageDto.GuildId }))
                {
                    continue;
                }

                if (!await _mediator.Send(new ChannelExistsRequest { Id = messageDto.ChannelId }))
                {
                    continue;
                }

                var message = new Message()
                {
                    Id = messageDto.Id,
                    GuildId = messageDto.GuildId,
                    UserId = messageDto.UserId,
                    ChannelId = messageDto.ChannelId
                };

                var time = LocalDateTimePattern.ExtendedIso.Parse(messageDto.Time).Value;

                message.Contents.Add(new MessageContent
                {
                    MessageId = messageDto.Id,
                    Time = time,
                    Content = messageDto.Content
                });

                _context.Messages.Add(message);

                createdMessageIds.Add(messageDto.Id);
            }

            await _context.SaveChangesAsync();

            return QueryResult<IEnumerable<ulong>>.Success(createdMessageIds);

        }
    }
}
