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

        }
    }

    public class EmoteBoardPostDto : IResponseModel
    {

    }

    public class Query : IRequest<QueryResult<EmoteBoardPostDto>>
    {
        public ulong GuildId { get; set; }

        public required string Name { get; set; }

        public ulong MessageId { get; set; }
    }

    public class Handler : IRequestHandler<Query, QueryResult<EmoteBoardPostDto>>
    {

        private readonly IMediator _mediator;
        private readonly ClemBotContext _context;

        public Handler(IMediator mediator, ClemBotContext context)
        {
            _mediator = mediator;
            _context = context;
        }

        public async Task<QueryResult<EmoteBoardPostDto>> Handle(Query request, CancellationToken cancellationToken)
        {
            return QueryResult<EmoteBoardPostDto>.NotFound();
        }
    }
}
