using MediatR;

namespace ClemBot.Api.Services.Caching.EmoteBoardPosts.Models;

public class ClearEmoteBoardPostExistsRequest : IRequest<Unit>
{
    public int BoardId { get; init; }

    public ulong MessageId { get; init; }
}
