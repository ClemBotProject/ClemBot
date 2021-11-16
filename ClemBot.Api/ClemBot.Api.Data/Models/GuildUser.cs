namespace ClemBot.Api.Data.Models;

public class GuildUser
{
    public ulong GuildId { get; set; }
    public Guild Guild { get; set; }

    public ulong UserId { get; set; }
    public User User { get; set; }
}