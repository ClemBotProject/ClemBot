using ClemBot.Api.Common;
using FluentValidation;

namespace ClemBot.Api.Core.Features.EmoteBoardPosts.Bot;

public class Index
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

    public class Query : IRequest<QueryResult<List<EmoteBoardPostDto>>>
    {

    }
}
