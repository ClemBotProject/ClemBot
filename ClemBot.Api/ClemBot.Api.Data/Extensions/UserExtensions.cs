using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using ClemBot.Api.Common.Enums;
using ClemBot.Api.Data.Models;
using Microsoft.EntityFrameworkCore;

namespace ClemBot.Api.Data.Extensions;

public static class UserExtensions
{
    /// <summary>
    /// Extension Method to return the claims a user has in a given guild.
    /// Will return all claims if that user is an admin in the guild or the owner of the guild
    /// </summary>
    /// <param name="users"></param>
    /// <param name="guildId"></param>
    /// <param name="userId"></param>
    /// <returns></returns>
    public static async Task<IEnumerable<BotAuthClaims>> GetUserGuildClaimsAsync(
        this DbSet<User> users,
        ulong guildId,
        ulong userId) =>
            await users
                .Where(x => x.Id == userId && x.Roles
                    .Any(z => z.GuildId == guildId && (z.Admin || z.Guild.OwnerId == userId)))
                .AnyAsync()
               ? Enum.GetValues(typeof(BotAuthClaims)).Cast<BotAuthClaims>()
               : await users
                   .AsNoTracking()
                   .Where(x => x.Id == userId)
                   .SelectMany(
                       b => b.Roles
                           .Where(e => e.GuildId == guildId)
                           .SelectMany(
                               c => c.Claims.Select(
                                   d => d.Claim)))
                   .Distinct()
                   .ToListAsync();

    /// <summary>
    /// Extension method to get all a Users associated claims for every guild they are in
    /// </summary>
    /// <param name="users"></param>
    /// <param name="userId"></param>
    /// <returns></returns>
    public static async Task<Dictionary<ulong, IEnumerable<BotAuthClaims>>> GetUserClaimsAsync(
        this DbSet<User> users,
        ulong userId)
    {
        var userGuilds = await users
            .Where(y => y.Id == userId)
            .Select(x => x.Guilds.Select(z => z.Id))
            .FirstOrDefaultAsync();

        if (userGuilds is null)
        {
            return new Dictionary<ulong, IEnumerable<BotAuthClaims>>();
        }

        var dictionary = new Dictionary<ulong, IEnumerable<BotAuthClaims>>();
        foreach (var guild in userGuilds)
        {
            dictionary.Add(guild, await users.GetUserGuildClaimsAsync(guild, userId));
        }

        return dictionary;
    }
}
