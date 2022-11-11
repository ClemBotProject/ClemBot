namespace ClemBot.Api.Data.Models;

public class GuildUser
{
    public ulong GuildId { get; set; }
    public virtual Guild Guild { get; set; } = null!;

    public ulong UserId { get; set; }
    public User User { get; set; } = null!;
}
