using System.Collections.Generic;

namespace ClemBot.Api.Data.Models;

public class User
{
    public ulong Id { get; set; }

    public required string Name { get; set; }

    public List<Guild> Guilds { get; set; } = new();
    public List<GuildUser> GuildUsers { get; set; } = new();

    public List<Role> Roles { get; set; } = null!;
    public List<RoleUser> RoleUsers { get; set; } = null!;

    public List<Tag> Tags { get; set; } = new();

    public List<Message> Messages { get; set; } = new();

    public List<EmoteBoardPost> EmoteBoardPosts { get; set; } = new();
}
