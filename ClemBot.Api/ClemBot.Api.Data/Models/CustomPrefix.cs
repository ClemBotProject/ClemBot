namespace ClemBot.Api.Data.Models;

public class CustomPrefix
{
    public int Id { get; set; }

    public required string Prefix { get; set; }

    public ulong GuildId { get; set; }
    public Guild Guild { get; set; } = null!;
}
