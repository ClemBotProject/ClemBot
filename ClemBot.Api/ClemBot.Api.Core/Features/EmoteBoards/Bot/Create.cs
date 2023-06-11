using ClemBot.Api.Data.Contexts;
using ClemBot.Api.Data.Models;
using ClemBot.Api.Services.Caching.Channels.Models;
using ClemBot.Api.Services.Caching.EmoteBoards.Models;
using ClemBot.Api.Services.Caching.Guilds.Models;
using FluentValidation;
using Microsoft.EntityFrameworkCore;

namespace ClemBot.Api.Core.Features.EmoteBoards.Bot;

public class Create
{

    public class Validator : AbstractValidator<Command>
    {
        public Validator()
        {
            RuleFor(c => c.GuildId).NotNull();
            RuleFor(c => c.Name).NotNull().NotEmpty().Must(c => !c.Any(char.IsWhiteSpace));
            RuleFor(c => c.Emote).NotNull().NotEmpty().Must(c => !c.Any(char.IsWhiteSpace));
            RuleFor(c => c.ReactionThreshold).NotNull().Must(t => t > 0);
            RuleFor(c => c.AllowBotPosts).NotNull();
            RuleFor(c => c.Channels).NotNull().Must(l => l.Count > 0);
        }
    }

    public class Command : IRequest<QueryResult<Unit>>
    {
        public ulong GuildId { get; set; }

        public required string Name { get; set; }

        public required string Emote { get; set; }

        public uint ReactionThreshold { get; set; }

        public bool AllowBotPosts { get; set; }

        public required List<ulong> Channels { get; set; }
    }

    public class Handler : IRequestHandler<Command, QueryResult<Unit>>
    {

        private readonly IMediator _mediator;
        private readonly ClemBotContext _context;

        public Handler(IMediator mediator, ClemBotContext context)
        {
            _mediator = mediator;
            _context = context;
        }

        public async Task<QueryResult<Unit>> Handle(Command request, CancellationToken cancellationToken)
        {
            var guildExists = await _mediator.Send(new GuildExistsRequest
            {
                Id = request.GuildId
            });

            if (!guildExists)
            {
                return QueryResult<Unit>.NotFound();
            }

            foreach (var channelId in request.Channels)
            {
                var channelExists = await _mediator.Send(new ChannelExistsRequest
                {
                    Id = channelId
                });

                if (!channelExists)
                {
                    return QueryResult<Unit>.NotFound();
                }
            }

            var channels = await _context.Channels
                .Where(c => request.Channels.Contains(c.Id))
                .ToListAsync();

            await _context.EmoteBoards.AddAsync(new EmoteBoard
            {
                GuildId = request.GuildId,
                Name = request.Name,
                Emote = request.Emote,
                ReactionThreshold = request.ReactionThreshold,
                AllowBotPosts = request.AllowBotPosts,
                Channels = channels
            });

            await _context.SaveChangesAsync();

            await _mediator.Send(new ClearEmoteBoardsRequest
            {
                GuildId = request.GuildId
            });

            return QueryResult<Unit>.NoContent();
        }
    }
}
