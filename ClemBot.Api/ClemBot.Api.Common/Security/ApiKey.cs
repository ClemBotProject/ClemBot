namespace ClemBot.Api.Common.Security;

/// <summary>
/// Class to encapsulate the Api key to accept from the Bot process to
/// authorize requests
/// </summary>
public class ApiKey
{
    public string Key { get; init; } = null!;
}
