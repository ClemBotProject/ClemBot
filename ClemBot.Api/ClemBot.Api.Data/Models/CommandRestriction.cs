using ClemBot.Api.Common.Enums;

namespace ClemBot.Api.Data.Models;

public class CommandRestriction
{
    public int Id { get; set; }

    public required string CommandName { get; set; }

    public bool? SilentlyFail { get; set; }

    public CommandRestrictionType RestrictionType { get; set; }

    public ulong GuildId { get; set; }
    public Guild Guild { get; set; } = null!;

    public ulong? ChannelId { get; set; }
    public Channel? Channel { get; set; }

}
