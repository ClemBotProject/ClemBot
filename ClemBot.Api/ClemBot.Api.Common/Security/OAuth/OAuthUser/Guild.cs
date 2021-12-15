namespace ClemBot.Api.Common.Security.OAuth.OAuthUser;

public class Guild
{
    public string Id { get; init; } = null!;
    public string Name { get; init; } = null!;
    public string Icon { get; init; } = null!;
    public bool Owner { get; init; }
    public int Permissions { get; init; }
    public List<string> Features { get; init; } = null!;
    public List<string> Claims { get; set; } = new();
    public bool IsAdded { get; set; }
}
