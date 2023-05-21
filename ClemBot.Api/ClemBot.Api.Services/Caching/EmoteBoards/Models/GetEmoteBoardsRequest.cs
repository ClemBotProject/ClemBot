using System.Collections.Generic;
using ClemBot.Api.Data.Models;
using MediatR;

namespace ClemBot.Api.Services.Caching.EmoteBoards.Models;

public class GetEmoteBoardsRequest : IRequest<List<EmoteBoard>>
{
    public ulong GuildId { get; set; }
}
