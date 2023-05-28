using System.Collections.Generic;
using MediatR;

namespace ClemBot.Api.Services.Caching.EmoteBoards.Models;

public class EmoteBoardDto
{
    public ulong GuildId { get; init; }

    public string Name { get; init; }

    public string Emote { get; init; }

    public uint ReactionThreshold { get; init; }

    public bool AllowBotPosts { get; init; }

    public List<ulong> Channels { get; init; }
}

public class GetEmoteBoardsRequest : IRequest<List<EmoteBoardDto>>
{
    public ulong GuildId { get; init; }
}
