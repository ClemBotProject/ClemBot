using System.Collections.Generic;

namespace ClemBot.Api.Data.Models;

public class EmoteBoard
{
    public int Id { get; set; }

    public ulong GuildId { get; set; }
    public Guild Guild { get; set; } = null!;

    public string Name { get; set; } = null!;

    public string Emote { get; set; } = null!;

    public uint ReactionThreshold { get; set; } = 4;

    public bool AllowBotPosts { get; set; }

    public List<EmoteBoardPost> Posts { get; set; } = new();

    public List<EmoteBoardChannelMapping> ChannelMappings { get; set; } = new();
}
