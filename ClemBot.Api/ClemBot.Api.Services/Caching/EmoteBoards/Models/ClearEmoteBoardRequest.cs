using MediatR;

namespace ClemBot.Api.Services.Caching.EmoteBoards.Models;

public class ClearEmoteBoardRequest : IRequest<Unit>
{
    public ulong GuildId { get; init; }

    public string Name { get; init; }
}
