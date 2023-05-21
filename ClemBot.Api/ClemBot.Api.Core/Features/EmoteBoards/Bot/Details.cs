using ClemBot.Api.Common;

namespace ClemBot.Api.Core.Features.EmoteBoards.Bot;

public class Details
{
    public class EmoteBoardDto : IResponseModel
    {

    }

    public class Query : IRequest<QueryResult<EmoteBoardDto>>
    {

    }
}
