using ClemBot.Api.Common.Enums;

namespace ClemBot.Api.Data.Models;

public class GuildSetting
{
    public int Id { get; set; }

    public ConfigSettings Setting { get; set; }

    public string Value { get; set; } = null!;

    public Guild Guild { get; set; } = null!;
    public ulong GuildId { get; set; }
}
