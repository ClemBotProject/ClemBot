using System;

namespace ClemBot.Api.Data.Models;

public class Reminder
{
    public int Id { get; set; }

    public string Link { get; set; }

    public DateTime Time { get; set; }

    public ulong MessageId { get; set; }
    public Guild Message { get; set; }

    public ulong UserId { get; set; }
    public User User { get; set; }
}