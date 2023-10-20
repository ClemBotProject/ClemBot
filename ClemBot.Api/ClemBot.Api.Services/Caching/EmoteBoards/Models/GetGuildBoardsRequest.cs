using System.Collections.Generic;
using MediatR;

namespace ClemBot.Api.Services.Caching.EmoteBoards.Models;

public class GetGuildBoardsRequest : IRequest<Dictionary<string, string>>
{
    public ulong GuildId { get; init; }
}
