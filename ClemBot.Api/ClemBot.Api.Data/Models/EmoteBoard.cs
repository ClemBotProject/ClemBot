using System.Collections.Generic;

namespace ClemBot.Api.Data.Models;

public class EmoteBoard
{
    public int Id { get; set; }

    public ulong GuildId { get; set; }
    public Guild Guild { get; set; } = null!;

    public required string Name { get; set; }

    public required string Emote { get; set; }

    public uint ReactionThreshold { get; set; } = 4;

    public bool AllowBotPosts { get; set; }

    public List<Channel> Channels { get; set; } = new();
}
