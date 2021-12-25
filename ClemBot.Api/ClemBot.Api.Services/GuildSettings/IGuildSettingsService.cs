using System;
using System.Collections.Generic;
using System.Threading.Tasks;
using ClemBot.Api.Common.Enums;

namespace ClemBot.Api.Services.GuildSettings;

public interface IGuildSettingsService
{
    Task<bool> GetCanEmbedLink(ulong guildId);
    Task<bool> SetCanEmbedLink(ulong guildId, bool val);
    Task<Dictionary<ConfigSettings, object>> GetAllSettingsAsync(ulong guildId);
}
