using System.Collections.Generic;

namespace ClemBot.Api.Data.Models;

public class Channel
{
    public ulong Id { get; set; }

    public string Name { get; set; }

    public ulong GuildId { get; set; }
    public Guild Guild { get; set; }

    public ulong? ParentId { get; set; }
    public Channel? Parent { get; set; }

    public bool IsThread { get; private set; }

    public List<Message> Messages { get; set; } = new();

    public List<DesignatedChannelMapping> DesignatedChannels { get; set; } = new();
}