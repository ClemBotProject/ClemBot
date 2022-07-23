using System;

namespace ClemBot.Api.Data.Models;

public class Reminder
{
    public int Id { get; set; }

    public Guid TaskId { get; set; }

    public string Link { get; set; }

    public string? Content { get; set; }

    public DateTime Time { get; set; }

    public bool Dispatched { get; set; } = false;

    public ulong MessageId { get; set; }
    public Message Message { get; set; }

    public ulong UserId { get; set; }
    public User User { get; set; }
}
