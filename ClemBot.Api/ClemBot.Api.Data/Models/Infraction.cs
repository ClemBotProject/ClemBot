using System;
using ClemBot.Api.Common.Enums;
using NodaTime;

namespace ClemBot.Api.Data.Models;

public class Infraction
{
    public int Id { get; set; }

    public required InfractionType Type { get; set; }

    public string? Reason { get; set; }

    public bool? IsActive { get; set; }

    public LocalDateTime? Duration { get; set; }

    public required LocalDateTime Time { get; set; }

    public ulong GuildId { get; set; }
    public Guild Guild { get; set; } = null!;

    public ulong AuthorId { get; set; }
    public User Author { get; set; } = null!;

    public ulong SubjectId { get; set; }
    public User Subject { get; set; } = null!;
}
