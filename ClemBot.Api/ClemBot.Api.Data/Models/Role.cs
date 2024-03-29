using System.Collections.Generic;

namespace ClemBot.Api.Data.Models;

public class Role
{
    public ulong Id { get; set; }

    public required string Name { get; set; }

    public bool IsAssignable { get; set; }

    public bool IsAutoAssigned { get; set; }

    public bool Admin { get; set; }

    public ulong GuildId { get; set; }
    public Guild Guild { get; set; } = null!;

    public List<User> Users { get; set; } = null!;
    public List<RoleUser> RoleUsers { get; set; } = null!;

    public List<ClaimsMapping> Claims { get; set; } = null!;
}
