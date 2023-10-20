using MediatR;

namespace ClemBot.Api.Services.Caching.EmoteBoards.Models;

public class ClearGuildBoardsRequest : IRequest<Unit>
{
    public ulong GuildId { get; init; }
}
