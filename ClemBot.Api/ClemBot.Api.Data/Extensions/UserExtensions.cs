using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using ClemBot.Api.Data.Enums;
using ClemBot.Api.Data.Models;
using Microsoft.EntityFrameworkCore;

namespace ClemBot.Api.Data.Extensions;

public static class UserExtensions
{
    public static async Task<IEnumerable<BotAuthClaims>> GetUserGuildClaimsAsync(
        this DbSet<User> users,
        ulong guildId,
        ulong userId) =>
        await users
            .Where(x => x.Id == userId)
            .Include(
                y => y.Roles.Where(z => z.GuildId == guildId))
            .ThenInclude(a => a.Claims)
            .SelectMany(
                b => b.Roles.SelectMany(
                    c => c.Claims.Select(
                        d => d.Claim)))
            .ToListAsync();

    public static async Task<Dictionary<ulong, IEnumerable<BotAuthClaims>>> GetUserClaimsAsync(
        this DbSet<User> users,
        ulong userId)
    {
        var user = await users
            .Where(x => x.Id == userId)
            .Include(y => y.Roles)
            .ThenInclude(a => a.Claims)
            .ThenInclude(z => z.Role)
            .SelectMany(
                b => b.Roles.SelectMany(
                    c => c.Claims))
            .ToListAsync();

            return user
                .GroupBy(v => v.Role.GuildId)
                .ToDictionary(g => g.Key, g => g.Select(x => x.Claim));
    }
}
