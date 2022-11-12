using ClemBot.Api.Common.Enums;

namespace ClemBot.Api.Data.Models;

public class DesignatedChannelMapping
{
    public int Id { get; set; }

    public required DesignatedChannels Type { get; set; }

    public ulong ChannelId { get; set; }
    public Channel Channel { get; set; } = null!;
}
