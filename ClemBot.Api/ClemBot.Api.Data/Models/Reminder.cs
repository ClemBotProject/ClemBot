using NodaTime;

namespace ClemBot.Api.Data.Models;

public class Reminder
{
    public int Id { get; set; }

    public required string Link { get; set; }

    public string? Content { get; set; }

    public LocalDateTime Time { get; set; }

    public bool Dispatched { get; set; } = false;

    public ulong UserId { get; set; }
    public virtual User User { get; set; } = null!;
}
