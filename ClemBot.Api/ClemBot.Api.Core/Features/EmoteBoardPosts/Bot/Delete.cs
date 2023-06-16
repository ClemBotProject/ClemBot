using ClemBot.Api.Data.Contexts;
using ClemBot.Api.Services.Caching.EmoteBoardPosts.Models;
using ClemBot.Api.Services.Caching.Guilds.Models;
using FluentValidation;
using LinqToDB;

namespace ClemBot.Api.Core.Features.EmoteBoardPosts.Bot;

public class Delete
{
    public class Validator : AbstractValidator<Command>
    {
        public Validator()
        {
            RuleFor(c => c.GuildId).NotNull();
            RuleFor(c => c.MessageId).NotNull();
        }
    }

    public class Command : IRequest<QueryResult<Unit>>
    {
        public ulong GuildId { get; set; }

        public ulong MessageId { get; set; }
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

            var posts = await _context.EmoteBoardPosts
                .Where(p => p.MessageId == request.MessageId)
                .ToListAsync();

            if (posts.Count == 0)
            {
                return QueryResult<Unit>.NotFound();
            }

            _context.EmoteBoardPosts.RemoveRange(posts);
            await _context.SaveChangesAsync();

            foreach (var post in posts)
            {
                await _mediator.Send(new ClearEmoteBoardPostRequest
                {
                    BoardId = post.EmoteBoardId,
                    MessageId = request.MessageId
                });
            }

            return QueryResult<Unit>.NoContent();
        }
    }
}
