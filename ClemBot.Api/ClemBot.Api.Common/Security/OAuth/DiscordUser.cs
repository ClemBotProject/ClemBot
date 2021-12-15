using System.Text.Json.Serialization;

namespace ClemBot.Api.Common.Security.OAuth
{
    public class DiscordUser
    {
        [JsonPropertyName("id")]
        public string? Id { get; set; }

        [JsonPropertyName("username")]
        public string? Username { get; set; }

        [JsonPropertyName("avatar")]
        public string? Avatar { get; set; }

        [JsonPropertyName("discriminator")]
        public string? Discriminator { get; set; }

        [JsonPropertyName("public_flags")]
        public int PublicFlags { get; set; }
    }}
