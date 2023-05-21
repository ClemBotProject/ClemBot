namespace ClemBot.Api.Data.Models;

public class EmoteBoardReaction
{
    public ulong UserId { get; set; }
    public User User { get; set; } = null!;

    public int EmoteBoardPostId { get; set; }
    public EmoteBoardPost EmoteBoardPost { get; set; } = null!;
}
