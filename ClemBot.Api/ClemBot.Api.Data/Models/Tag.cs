using System;
using System.Collections.Generic;
using NodaTime;

namespace ClemBot.Api.Data.Models;

public class Tag
{
    public int Id { get; set; }

    public string Name { get; set; }

    public string Content { get; set; }

    public LocalDateTime Time { get; set; }

    public ulong GuildId { get; set; }
    public Guild Guild { get; set; }

    public ulong UserId { get; set; }
    public User User { get; set; }

    public List<TagUse> TagUses { get; set; } = new();
}