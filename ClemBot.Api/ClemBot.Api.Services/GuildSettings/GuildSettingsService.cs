using System;
using System.Collections.Generic;
using System.Linq;
using System.Text.Json;
using System.Text.Json.Serialization;
using System.Threading.Tasks;
using ClemBot.Api.Common.Enums;
using ClemBot.Api.Data.Contexts;
using ClemBot.Api.Data.Models;
using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.Logging;

namespace ClemBot.Api.Services.GuildSettings;

public class GuildSettingsService : IGuildSettingsService
{
    private readonly ClemBotContext _context;

    private readonly ILogger<GuildSettingsService> _logger;

    public GuildSettingsService(ClemBotContext context, ILogger<GuildSettingsService> logger)
    {
        _context = context;
        _logger = logger;
    }

    public async Task<Dictionary<ConfigSettings, object>> GetAllSettingsAsync(ulong guildId)
    {
        var values = new Dictionary<ConfigSettings, object>();
        foreach (var e in Enum.GetValues<ConfigSettings>())
        {
            values[e] = await GetPropertyAsync<object>(e, guildId);
        }
        return values;
    }

    public async Task<T> GetPropertyAsync<T>(ConfigSettings configSetting, ulong guildId)
    {
        _logger.LogInformation("Getting Guild: {Id} Config {Setting}", guildId, configSetting);
        var val = await _context.GuildSettings
            .AsNoTracking()
            .FirstOrDefaultAsync(x => x.GuildId == guildId && x.Setting == configSetting);

        if (val?.Value is null)
        {
            return (T)GuildConfig.TypeMappings[configSetting].Default;
        }

        return (T)GuildConfig.TypeMappings[ConfigSettings.allow_embed_links].Deserialize(val.Value);

    }

    public Task<object> GetPropertyAsync(ConfigSettings configSetting, ulong guildId)
        => GetPropertyAsync<object>(configSetting, guildId);

    public async Task<bool> SetPropertyAsync(ConfigSettings configSetting, ulong guildId, string value)
    {
        _logger.LogInformation("Setting Guild: {Id} Config {Setting} with Value: {Value}", guildId, configSetting, value);

        var config = GuildConfig.TypeMappings[configSetting];

        try
        {
            // Call the deserialize method on the string representation so that we can be sure its valid with a given serializer
            _ = config.Deserialize(value);
        }
        catch (Exception e)
        {
            _logger.LogError(e, "Expected {Type} for Guild Setting {Setting}; Found {SettingType}",
                config.Type,
                configSetting,
                value);
            return false;
        }

        var settingEntity = await _context.GuildSettings
                .FirstOrDefaultAsync(x => x.GuildId == guildId && x.Setting == configSetting);

        if (settingEntity is not null)
        {
            settingEntity.Value = value;
            await _context.SaveChangesAsync();
            return true;
        }

        _context.GuildSettings.Add(new GuildSetting
        {
            Setting = configSetting,
            Value = value,
            GuildId = guildId
        });
        await _context.SaveChangesAsync();
        return true;

    }
}
