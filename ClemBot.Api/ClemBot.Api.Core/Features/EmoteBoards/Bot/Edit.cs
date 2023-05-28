using ClemBot.Api.Data.Contexts;
using ClemBot.Api.Data.Models;
using ClemBot.Api.Services.Caching.EmoteBoards.Models;
using ClemBot.Api.Services.Caching.Guilds.Models;
using FluentValidation;
using Microsoft.EntityFrameworkCore;

namespace ClemBot.Api.Core.Features.EmoteBoards.Bot;

public class Edit
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
            RuleForEach(c => c.Channels).NotNull().Must(channel => channel > 0);
        }
    }

    public class Command : IRequest<QueryResult<Unit>>
    {
        public ulong GuildId { get; set; }

        public string Name { get; set; } = null!;

        public string Emote { get; set; } = null!;

        public uint ReactionThreshold { get; set; }

        public bool AllowBotPosts { get; set; }

        public List<ulong> Channels { get; set; } = null!;
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

            var emoteBoard = await _context.EmoteBoards
                .Where(b => b.GuildId == request.GuildId
                            && string.Equals(b.Name, request.Name, StringComparison.OrdinalIgnoreCase))
                .FirstOrDefaultAsync();

            if (emoteBoard is null)
            {
                return QueryResult<Unit>.NotFound();
            }

            // check for emote conflicts within the guild
            var similar = await _context.EmoteBoards
                .AnyAsync(eb => eb.GuildId == request.GuildId
                                && string.Equals(eb.Emote, request.Emote, StringComparison.OrdinalIgnoreCase));

            if (similar)
            {
                return QueryResult<Unit>.Conflict();
            }

            emoteBoard.Emote = request.Emote;
            emoteBoard.ReactionThreshold = request.ReactionThreshold;
            emoteBoard.AllowBotPosts = request.AllowBotPosts;

            var currentChannels = await _context.EmoteBoardChannelMappings
                .Where(cm => cm.EmoteBoardId == emoteBoard.Id)
                .Select(cm => cm.ChannelId)
                .ToListAsync();

            var nonintersections = currentChannels.Except(request.Channels).Union(request.Channels.Except(currentChannels));

            foreach (var channelId in nonintersections)
            {
                if (!request.Channels.Contains(channelId))
                {
                    // remove the channel id from our mappings
                    var mapping = await _context.EmoteBoardChannelMappings
                        .Where(cm => cm.EmoteBoardId == emoteBoard.Id && cm.ChannelId == channelId)
                        .FirstOrDefaultAsync();

                    if (mapping is null)
                    {
                        continue;
                    }

                    _context.EmoteBoardChannelMappings.Remove(mapping);
                }
                else
                {
                    await _context.EmoteBoardChannelMappings.AddAsync(new EmoteBoardChannelMapping
                    {
                        EmoteBoardId = emoteBoard.Id, ChannelId = channelId
                    });
                }
            }

            await _context.SaveChangesAsync();

            await _mediator.Send(new ClearEmoteBoardsRequest
            {
                GuildId = request.GuildId
            });

            return QueryResult<Unit>.NoContent();
        }
    }
}
