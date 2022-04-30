using System.Collections.Generic;
using System.Reflection;

namespace ClemBot.Api.Data.Models;

public class Guild
{
    public ulong Id { get; set; }

    public string Name { get; set; }

    public string? WelcomeMessage { get; set; }

    public ulong OwnerId { get; set; }

    public List<User> Users { get; set; } = new();
    public List<GuildUser> GuildUsers { get; set; } = new();

    public List<Channel> Channels { get; set; } = new();

    public List<Message> Messages { get; set; } = new();

    public List<Tag> Tags { get; set; } = new();

    public List<Role> Roles { get; set; } = new();

    public List<Infraction> Infractions { get; set; } = new();

    public List<Reminder> Reminders { get; set; } = new();

    public List<CustomPrefix> CustomPrefixes { get; set; } = new();

    public List<CustomTagPrefix> CustomTagPrefixes { get; set; } = new();

    public List<GuildSetting> GuildSettings { get; set; } = new();
}
