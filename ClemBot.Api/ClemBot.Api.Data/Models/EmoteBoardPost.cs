using System.Collections.Generic;

namespace ClemBot.Api.Data.Models;

public class EmoteBoardPost
{
    public ulong Id { get; set; }

    public ulong UserId { get; set; }
    public User User { get; set; } = null!;

    public ulong MessageId { get; set; }

    public int EmoteBoardId { get; set; }
    public EmoteBoard EmoteBoard { get; set; } = null!;

    public List<EmoteBoardMessage> Messages { get; set; } = new();

    public List<EmoteBoardReaction> Reactions { get; set; } = new();
}
