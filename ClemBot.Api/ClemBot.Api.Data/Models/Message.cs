using System;
using System.Collections.Generic;


namespace ClemBot.Api.Data.Models;

public class Message
{
    public ulong Id { get; set; }

    public List<MessageContent> Contents { get; set; } = new();

    public ulong GuildId { get; set; }
    public Guild Guild { get; set; }

    public ulong ChannelId { get; set; }
    public Channel Channel { get; set; }

    public ulong UserId { get; set; }
    public User User { get; set; }
}