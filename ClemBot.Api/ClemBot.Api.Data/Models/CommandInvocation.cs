using System;
using NodaTime;

namespace ClemBot.Api.Data.Models;

public class CommandInvocation
{
    public int Id { get; set; }

    public string CommandName { get; set; } = null!;

    public LocalDateTime Time { get; set; }

    public ulong GuildId { get; set; }

    public ulong ChannelId { get; set; }

    public ulong UserId { get; set; }
}
