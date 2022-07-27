using System;
using System.Collections.Generic;
using System.Threading.Tasks;
using ClemBot.Api.Common.Enums;

namespace ClemBot.Api.Services.GuildSettings;

public interface IGuildSettingsService
{
    /// <summary>
    /// Gets all guild settings for every enum value
    /// </summary>
    /// <param name="guildId"></param>
    /// <returns></returns>
    Task<Dictionary<ConfigSettings, object>> GetAllSettingsAsync(ulong guildId);

    /// <summary>
    /// Get a specific guild setting as a specified generic type
    /// </summary>
    /// <param name="configSetting">Name of the setting to retrieve</param>
    /// <param name="guildId">Guild to get the setting for</param>
    /// <typeparam name="T"></typeparam>
    /// <returns></returns>
    Task<T> GetPropertyAsync<T>(ConfigSettings configSetting, ulong guildId);

    /// <summary>
    /// Gets a specific guild setting as an object type
    /// </summary>
    /// <param name="configSetting">Name of the setting to retrieve</param>
    /// <param name="guildId">Guild to get the setting for</param>
    /// <returns></returns>
    Task<object> GetPropertyAsync(ConfigSettings configSetting, ulong guildId);

    /// <summary>
    /// Sets a config setting to a string value representing the object
    /// </summary>
    /// <param name="configSetting"></param>
    /// <param name="guildId"></param>
    /// <param name="value"></param>
    /// <returns></returns>
    Task<bool> SetPropertyAsync(ConfigSettings configSetting, ulong guildId, string value);
}
