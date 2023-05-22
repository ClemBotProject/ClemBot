using MediatR;

namespace ClemBot.Api.Services.Caching.EmoteBoards.Models;

public class ClearEmoteBoardChannelsRequest : IRequest<Unit>
{
    public int EmoteBoardId { get; init; }
}
