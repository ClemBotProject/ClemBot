using ClemBot.Api.Data.Models;
using MediatR;

namespace ClemBot.Api.Services.Caching.EmoteBoards.Models;

public class GetEmoteBoardRequest : IRequest<EmoteBoard>
{
    public ulong GuildId { get; init; }

    public string Name { get; init; }
}
