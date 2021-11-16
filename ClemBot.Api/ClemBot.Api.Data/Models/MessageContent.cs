using System;
using NodaTime;

namespace ClemBot.Api.Data.Models;

public class MessageContent
{
    public int Id { get; set; }

    public string Content { get; set; }

    public LocalDateTime Time { get; set; }

    public ulong MessageId { get; set; }
    public Message Message { get; set; }
}