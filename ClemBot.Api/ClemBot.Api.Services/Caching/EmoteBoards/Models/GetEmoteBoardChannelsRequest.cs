using System.Collections.Generic;
using MediatR;

namespace ClemBot.Api.Services.Caching.EmoteBoards.Models;

public class GetEmoteBoardChannelsRequest : IRequest<List<ulong>>
{
    public int EmoteBoardId { get; init; }
}
