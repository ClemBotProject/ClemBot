namespace ClemBot.Api.Common.Security.OAuth.OAuthUser
{
    public class Application
    {
        public string Id { get; set; } = null!;
        public string Name { get; set; }= null!;
        public string Icon { get; set; }= null!;
        public string Description { get; set; }= null!;
        public string Summary { get; set; }= null!;
        public bool Hook { get; set; }
        public bool BotPublic { get; set; }
        public bool BotRequireCodeGrant { get; set; }
        public string VerifyKey { get; set; }= null!;
    }
}
