namespace ClemBot.Api.Common.Security.OAuth.OAuthUser
{
    public class DiscordOAuthModel
    {
        public Application Application { get; set; } = null!;
        public List<string>? Scopes { get; set; }
        public DateTime Expires { get; set; }
        public User User { get; set; } = null!;
    }
}
