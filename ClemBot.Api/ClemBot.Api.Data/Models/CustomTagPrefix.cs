namespace ClemBot.Api.Data.Models;

public class CustomTagPrefix
{
    public int Id { get; set; }

    public string TagPrefix { get; set; }

    public ulong GuildId { get; set; }
    public Guild Guild { get; set; }
}
