using System;

namespace ClemBot.Api.Data.Models
{
    public class CommandInvocation
    {
        public int Id { get; set; }

        public string CommandName { get; set; } = null!;

        public DateTime Time { get; set; }

        public Guild Guild { get; set; }
        public ulong GuildId { get; set; }

        public Channel Channel { get; set; }
        public ulong ChannelId { get; set; }

        public User User { get; set; }
        public ulong UserId { get; set; }
    }
}
