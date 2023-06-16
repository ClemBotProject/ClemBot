using ClemBot.Api.Common;
using ClemBot.Api.Data.Contexts;
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
            return QueryResult<List<EmoteBoardPostDto>>.NotFound();
        }
    }
}
