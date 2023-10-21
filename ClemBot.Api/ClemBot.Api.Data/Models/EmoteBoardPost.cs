using System.Collections.Generic;

namespace ClemBot.Api.Data.Models;

/// <summary>
/// Represents a message (typically user-generated) that received enough reactions to be posted.
/// </summary>
public class EmoteBoardPost
{
    public int Id { get; set; }

    public ulong UserId { get; set; }
    public User User { get; set; } = null!;

    public ulong MessageId { get; set; }

    public ulong ChannelId { get; set; }
    public Channel Channel { get; set; } = null!;

    public int EmoteBoardId { get; set; }
    public EmoteBoard EmoteBoard { get; set; } = null!;

    public List<EmoteBoardPostReaction> Reactions { get; set; } = new();

    public List<EmoteBoardMessage> Messages { get; set; } = null!;
}
