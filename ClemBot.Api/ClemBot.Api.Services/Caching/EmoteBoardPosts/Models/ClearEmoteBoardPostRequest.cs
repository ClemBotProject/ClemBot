using MediatR;

namespace ClemBot.Api.Services.Caching.EmoteBoardPosts.Models;

public class ClearEmoteBoardPostRequest : IRequest<Unit>
{
    public int BoardId { get; init; }

    public ulong MessageId { get; init; }
}
