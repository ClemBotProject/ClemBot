using ClemBot.Api.Common.Enums;

namespace ClemBot.Api.Data.Models;

public class ClaimsMapping
{
    public int Id { get; set; }

    public required BotAuthClaims Claim { get; set; }

    public ulong RoleId { get; set; }
    public Role Role { get; set; } = null!;
}
