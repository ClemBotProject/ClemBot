namespace ClemBot.Api.Data.Models;

/// <summary>
/// Represents a message (typically an embed) sent by ClemBot to one EmoteBoard channel.
/// </summary>
public class EmoteBoardMessage
{
    public int Id { get; set; }

    public ulong MessageId { get; set; }

    public ulong ChannelId { get; set; }
    public Channel Channel { get; set; } = null!;

    public int EmoteBoardPostId { get; set; }
    public EmoteBoardPost EmoteBoardPost { get; set; } = null!;
}
