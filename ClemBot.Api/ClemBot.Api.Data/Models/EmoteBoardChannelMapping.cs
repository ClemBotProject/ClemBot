using System.Collections.Generic;

namespace ClemBot.Api.Data.Models;

public class EmoteBoardChannelMapping
{
    public ulong ChannelId { get; set; }
    public Channel Channel { get; set; } = null!;

    public int EmoteBoardId { get; set; }
    public EmoteBoard EmoteBoard { get; set; } = null!;

    public List<EmoteBoardMessage> Messages { get; set; } = new();
}
