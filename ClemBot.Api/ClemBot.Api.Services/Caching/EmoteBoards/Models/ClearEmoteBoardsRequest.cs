using MediatR;

namespace ClemBot.Api.Services.Caching.EmoteBoards.Models;

public class ClearEmoteBoardsRequest : IRequest<Unit>
{
    public ulong GuildId { get; set; }
}
