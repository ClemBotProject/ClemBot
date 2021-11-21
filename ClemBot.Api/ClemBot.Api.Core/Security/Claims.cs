namespace ClemBot.Api.Core.Security;

public static class Claims
{
    public static string BotApiKey => "BotClaim";
    public static string ContextGuildId => "ContextGuildId";
    public static string DiscordBearer => "DiscordBearer";
    public static string UserId => "UserId";
}
