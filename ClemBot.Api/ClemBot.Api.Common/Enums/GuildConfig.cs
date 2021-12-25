using System.Text.Json;

namespace ClemBot.Api.Common.Enums;

public enum ConfigSettings
{
    /// <summary>
    /// Setting to specify if a server allows for the bot to
    /// automatically embed message links
    /// </summary>
    allow_embed_links
}

public static class GuildConfig
{
    /// <summary>
    /// Metadata type for defining how a config value can be manipulated
    /// </summary>
    public record ConfigMetaData
    {
        public Func<string, object> Deserialize { get; }

        public Func<object, string> Serialize { get; }

        /// <summary>
        /// Type that a given setting must be after deserializing
        /// </summary>
        public Type Type { get; init; }

        /// <summary>
        /// The default value for a setting. This is required because
        /// we only insert a setting once its set by a user
        /// </summary>
        public object Default { get; init; }

        /// <summary>
        /// Standard constructor to create a meta data type with a default value
        /// Defaults to System.Text.Json serialization for values
        /// </summary>
        /// <param name="type"></param>
        /// <param name="default"></param>
        /// <exception cref="JsonException"></exception>
        public ConfigMetaData(Type type, object @default)
        {
            Type = type;
            Default = @default;
            Deserialize = s => JsonSerializer.Deserialize(s, Type)
                             ?? throw new JsonException("Attempting to deserialize config data failed");
            Serialize = s => JsonSerializer.Serialize(s);
        }

        /// <summary>
        /// Overloaded constructor to allow for config values to have a specified Serialize
        /// and deserialize implementation
        /// </summary>
        /// <param name="type"></param>
        /// <param name="serialize"></param>
        /// <param name="deserialize"></param>
        /// <param name="default"></param>
        public ConfigMetaData(Type type, Func<object, string> serialize, Func<string, object> deserialize, object @default)
        {
            Serialize = serialize;
            Deserialize = deserialize;
            Type = type;
            Default = @default;
        }
    }

    /// <summary>
    /// Mappings to define how to interact with a given config value
    /// </summary>
    public static readonly IReadOnlyDictionary<ConfigSettings, ConfigMetaData> TypeMappings
        = new Dictionary<ConfigSettings, ConfigMetaData>
    {
        { ConfigSettings.allow_embed_links, new ConfigMetaData(typeof(bool), false) }
    };
}
