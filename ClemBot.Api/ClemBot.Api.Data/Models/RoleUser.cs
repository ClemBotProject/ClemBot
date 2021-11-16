namespace ClemBot.Api.Data.Models;

public class RoleUser
{
    public ulong RoleId { get; set; }
    public Role Role { get; set; }

    public ulong UserId { get; set; }
    public User User { get; set; }
}