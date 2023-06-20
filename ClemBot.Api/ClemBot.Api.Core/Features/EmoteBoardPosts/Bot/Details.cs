using ClemBot.Api.Common;
using ClemBot.Api.Data.Contexts;
using ClemBot.Api.Data.Models;
using ClemBot.Api.Services.Caching.EmoteBoards.Models;
using ClemBot.Api.Services.Caching.Guilds.Models;
using ClemBot.Api.Services.Caching.Messages.Models;
using FluentValidation;

namespace ClemBot.Api.Core.Features.EmoteBoardPosts.Bot;

public class Details
{
    public class Validator : AbstractValidator<Query>
    {
        public Validator()
        {
            RuleFor(q => q.GuildId).NotNull();
            RuleFor(q => q.MessageId).NotNull();
            RuleFor(q => q.Name).Must(s => s is null || !s.Any(char.IsWhiteSpace));
        }
    }

    public class EmoteBoardPostDto : IResponseModel
    {
        public required string Name { get; init; }

        public ulong ChannelId { get; init; }

        public ulong MessageId { get; init; }

        public ulong UserId { get; init; }

        public required List<ulong> Reactions { get; init; }

        public required Dictionary<ulong, ulong> ChannelMessageIds { get; init; }
    }

    public class Query : IRequest<QueryResult<List<EmoteBoardPostDto>>>
    {
        public ulong GuildId { get; set; }

        public string? Name { get; set; }

        public ulong MessageId { get; set; }
    }

    public class Handler : IRequestHandler<Query, QueryResult<List<EmoteBoardPostDto>>>
    {

        private readonly IMediator _mediator;
        private readonly ClemBotContext _context;

        public Handler(IMediator mediator, ClemBotContext context)
        {
            _mediator = mediator;
            _context = context;
        }

        public async Task<QueryResult<List<EmoteBoardPostDto>>> Handle(Query request, CancellationToken cancellationToken)
        {
            var guildExists = await _mediator.Send(new GuildExistsRequest
            {
                Id = request.GuildId
            });

            if (!guildExists)
            {
                return QueryResult<List<EmoteBoardPostDto>>.NotFound();
            }

            var messageExists = await _mediator.Send(new MessageExistsRequest
            {
                Id = request.MessageId
            });

            if (!messageExists)
            {
                return QueryResult<List<EmoteBoardPostDto>>.NotFound();
            }

            EmoteBoard? board = null;

            if (request.Name is not null)
            {
                var boards = await _mediator.Send(new GetEmoteBoardsRequest
                {
                    GuildId = request.GuildId
                });

                board = boards.FirstOrDefault(b => string.Equals(b.Name, request.Name, StringComparison.OrdinalIgnoreCase));

                if (board is null)
                {
                    return QueryResult<List<EmoteBoardPostDto>>.NotFound();
                }
            }

            var posts = await _context.EmoteBoardPosts
                .Where(p => board != null ? p.EmoteBoardId == board.Id : p.EmoteBoard.GuildId == request.GuildId)
                .Where(p => p.MessageId == request.MessageId)
                .Select(p => new EmoteBoardPostDto
                {
                    ChannelId = p.ChannelId,
                    MessageId = p.MessageId,
                    Name = p.EmoteBoard.Name,
                    
                })

            return QueryResult<List<EmoteBoardPostDto>>.NotFound();
        }
    }
}
