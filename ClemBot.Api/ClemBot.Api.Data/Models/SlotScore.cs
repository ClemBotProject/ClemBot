using System;
using NodaTime;

namespace ClemBot.Api.Data.Models;

public class SlotScore
{
    public int Id { get; set; }

    public ulong Score { get; set; }

    public LocalDateTime Time { get; set; }
    public ulong? MessageId { get; set; }

    public Guild Guild { get; set; } = null!;
    public ulong GuildId { get; set; }

    public User User { get; set; } = null!;
    public ulong UserId { get; set; }

    public ulong? ChannelId { get; set; }
    public Channel? Channel { get; set; } = null!;
}
