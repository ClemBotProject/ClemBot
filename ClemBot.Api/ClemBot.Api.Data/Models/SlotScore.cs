using System;
using NodaTime;

namespace ClemBot.Api.Data.Models;

public class SlotScore
{
    public int Id { get; set; }

    public ulong Score { get; set; }

    public LocalDateTime Time { get; set; }

    public Guild Guild { get; set; }
    public ulong GuildId { get; set; }

    public User User { get; set; }
    public ulong UserId { get; set; }
}
