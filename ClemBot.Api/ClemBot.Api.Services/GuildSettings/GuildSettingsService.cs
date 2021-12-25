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

    public async Task<bool> GetCanEmbedLink(ulong guildId)
        => await GetPropertyAsync<bool>(ConfigSettings.allow_embed_links, guildId);

    public async Task<bool> SetCanEmbedLink(ulong guildId, bool val)
        => await SetPropertyAsync(ConfigSettings.allow_embed_links, guildId, val);

    public async Task<Dictionary<ConfigSettings, object>> GetAllSettingsAsync(ulong guildId)
    {
        var values = new Dictionary<ConfigSettings, object>();
        foreach (var e in Enum.GetValues<ConfigSettings>())
        {
            values[e] = await GetPropertyAsync<object>(e, guildId);
        }
        return values;
    }

    private async Task<T> GetPropertyAsync<T>(ConfigSettings configSetting, ulong guildId)
    {
        _logger.LogInformation("Getting Guild: {Id} Config {Setting}", guildId, configSetting);
        var val = await _context.GuildSettings
            .AsNoTracking()
            .FirstOrDefaultAsync(x => x.GuildId == guildId && x.Setting == configSetting);

        if (val?.Value is not null)
        {
            return (T)GuildConfig.TypeMappings[ConfigSettings.allow_embed_links].Deserialize(val.Value);
        }

        return (T)GuildConfig.TypeMappings[configSetting].Default;
    }

    private async Task<bool> SetPropertyAsync<T>(ConfigSettings configSetting, ulong guildId, T value)
    {
        _logger.LogInformation("Setting Guild: {Id} Config {Setting} with {Value}", guildId, configSetting, value);
        var stringVal = JsonSerializer.Serialize(value);

        var type = GuildConfig.TypeMappings[configSetting].Type;

        if (typeof(T) != type)
        {
            _logger.LogError("Failed to convert {Type} to Guild Setting {Setting} with type of {SettingType}",
                value.GetType(),
                configSetting,
                value.GetType());
            return false;
        }

        var settingEntity = await _context.GuildSettings
                .FirstOrDefaultAsync(x => x.GuildId == guildId && x.Setting == configSetting);

        if (settingEntity is not null)
        {
            settingEntity.Value = GuildConfig.TypeMappings[configSetting].Serialize(value);
            await _context.SaveChangesAsync();
            return true;
        }

        _context.GuildSettings.Add(new GuildSetting
        {
            Setting = configSetting,
            Value = stringVal,
            GuildId = guildId
        });
        await _context.SaveChangesAsync();
        return true;

    }
}
