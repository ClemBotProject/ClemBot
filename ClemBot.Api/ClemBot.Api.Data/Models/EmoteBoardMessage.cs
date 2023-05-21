namespace ClemBot.Api.Data.Models;

/// <summary>
/// Represents a message (typically an embed) sent by ClemBot to one EmoteBoard channel.
/// </summary>
public class EmoteBoardMessage
{
    public int Id { get; set; }

    public int ChannelMappingId { get; set; }
    public EmoteBoardChannelMapping ChannelMapping { get; set; } = null!;

    public int EmoteBoardPostId { get; set; }
    public EmoteBoardPost EmoteBoardPost { get; set; } = null!;

    public ulong MessageId { get; set; }
}
