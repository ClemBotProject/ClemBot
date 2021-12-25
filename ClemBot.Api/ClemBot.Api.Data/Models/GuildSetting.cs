using ClemBot.Api.Common.Enums;

namespace ClemBot.Api.Data.Models;

public class GuildSetting
{
    public int Id { get; set; }

    public ConfigSettings Setting { get; set; }

    public string Value { get; set; }

    public Guild Guild { get; set; }
    public ulong GuildId { get; set; }
}
