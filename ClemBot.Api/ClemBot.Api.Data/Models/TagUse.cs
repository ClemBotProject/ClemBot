using System;

namespace ClemBot.Api.Data.Models;

public class TagUse
{
    public int Id { get; set; }

    public DateTime Time { get; set; }

    public ulong UserId { get; set; }
    public User User { get; set; } = null!;

    public int TagId { get; set; }
    public Tag Tag { get; set; } = null!;

    public ulong ChannelId { get; set; }
    public Channel Channel { get; set; } = null!;
}
