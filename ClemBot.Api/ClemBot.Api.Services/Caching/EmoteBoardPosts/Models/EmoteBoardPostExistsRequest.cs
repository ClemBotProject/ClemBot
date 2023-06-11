using MediatR;

namespace ClemBot.Api.Services.Caching.EmoteBoardPosts.Models;

public class EmoteBoardPostExistsRequest : IRequest<bool>
{
    public int BoardId { get; init; }

    public ulong MessageId { get; init; }
}
