namespace ClemBot.Api.Data.Models;

public class CommandRestriction
{

    public string CommandName { get; set; }

    public bool SilentlyFail { get; set; }

    public ulong GuildId { get; set; }
    public Guild Guild { get; set; }

    public ulong ChannelId { get; set; }
    public Channel? Channel { get; set; } = null!;

}
