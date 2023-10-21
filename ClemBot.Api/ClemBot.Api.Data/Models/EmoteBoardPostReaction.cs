namespace ClemBot.Api.Data.Models;

public class EmoteBoardPostReaction
{
    public int Id { get; set; }

    public int EmoteBoardPostId { get; set; }
    public EmoteBoardPost EmoteBoardPost { get; set; } = null!;

    public ulong UserId { get; set; }
}
